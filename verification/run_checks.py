"""run the evidence checks in separate processes, using the current python."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time


CHECKS = [
    ('syntax', 'check_syntax.py', None, 'source'),
    ('submission_audit', 'audit_submission.py', None, 'source'),
    ('template_preservation', 'check_template_preservation.py', None, 'source'),
    ('core_rules', 'check_core.py', 25, 'graphics stubs'),
    ('optional_features', 'check_extras.py', 15, 'graphics stubs'),
    ('sound_bank', 'check_sounds.py', 7, 'graphics and audio spies'),
    ('sound_events', 'check_sound_events.py', 9, 'graphics and audio spies'),
    ('colors_and_json', 'check_compatibility.py', None, 'real kivy'),
    ('app_audio', 'check_app_audio.py', 8, 'real kivy with audio spies'),
    ('loading', 'check_loading.py', 10, 'real kivy'),
    ('interface', 'check_interface.py', None, 'real kivy'),
    ('real_audio', 'real_sound_check.py', None, 'real kivy with dummy audio'),
    ('playthroughs', 'playthroughs.py', None, 'graphics stubs; scripted aim'),
]


def sha256(path):
    """hash the bytes of one file, because names alone do not bind a test run."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(folder):
    """return the files actually tested, leaving generated caches out."""
    return {
        path.relative_to(folder).as_posix(): {
            'sha256': sha256(path), 'bytes': path.stat().st_size
        }
        for path in sorted(folder.rglob('*'))
        if path.is_file() and '__pycache__' not in path.parts
        and path.name != '.DS_Store' and path.suffix != '.pyc'
    }


def version(package):
    """record an installed version without importing kivy into this process."""
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def main():
    """run every suite, keep its raw output, and fail if any check fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path,
                        help='path to the complete, unzipped shield folder')
    parser.add_argument('--output', type=Path,
                        help='evidence folder; defaults to verification/evidence')
    parser.add_argument('--headless', action='store_true',
                        help='use the SDL offscreen video driver on linux')
    parser.add_argument('--snapshots', action='store_true',
                        help='save all 32 interface screenshots')
    options = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    project = options.project.expanduser().resolve()
    output = (options.output or bundle / 'evidence').expanduser().resolve()
    if not (project / '__main__.py').is_file():
        parser.error('--project must contain __main__.py, app.py, and Data/')
    if options.headless and sys.platform != 'linux':
        parser.error('--headless is for linux; leave it off on mac or windows')
    output.mkdir(parents=True, exist_ok=True)
    logs = output / 'logs'
    logs.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update({
        'SHIELD_PROJECT': str(project),
        'SHIELD_EVIDENCE_OUTPUT': str(output),
        'KIVY_NO_ARGS': '1',
        'KIVY_NO_CONSOLELOG': '1',
        'PYTHONDONTWRITEBYTECODE': '1',
        'SDL_AUDIODRIVER': 'dummy',
    })
    if options.headless:
        env.update({'SDL_VIDEODRIVER': 'offscreen', 'KIVY_WINDOW': 'sdl2'})
    before = inventory(project)
    summary = {
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python': sys.version,
        'platform': platform.platform(),
        'dependencies': {'kivy': version('kivy'), 'introcs': version('introcs')},
        'headless': options.headless,
        'runtime_settings': {key: env.get(key) for key in [
            'KIVY_NO_ARGS', 'KIVY_NO_CONSOLELOG', 'PYTHONDONTWRITEBYTECODE',
            'SDL_AUDIODRIVER', 'SDL_VIDEODRIVER', 'KIVY_WINDOW']},
        'audio_driver': 'dummy',
        'audible_audio_verified': False,
        'project_file_count': len(before),
        'project_files': before,
        'check_files': inventory(bundle / 'checks'),
        'reference_manifest_sha256': sha256(bundle / 'starter_manifest.json'),
        'template_manifest_sha256': sha256(bundle / 'template_preservation_manifest.json'),
        'report_paths': {
            'interface': 'interface/interface_report.json',
            'compatibility': 'compatibility.json',
            'real_audio': 'real_audio.json',
            'playthroughs': 'playthroughs.json',
            'submission_audit': 'submission_audit.json',
            'template_preservation': 'template_preservation.json',
            'logs': 'logs/', 'screenshots': ['interface/', 'loading/'],
        },
        'suites': [],
    }
    for name, filename, expected, mode in CHECKS:
        print(f'running {name} ({mode})', flush=True)
        command = [sys.executable, str(bundle / 'checks' / filename)]
        if name == 'interface' and options.snapshots:
            command.append('--snapshots')
        started = time.monotonic()
        logfile = logs / (name + '.log')
        with logfile.open('w', encoding='utf-8') as stream:
            try:
                result = subprocess.run(command, cwd=bundle, env=env,
                                        stdout=stream, stderr=subprocess.STDOUT,
                                        timeout=180, check=False)
                returncode = result.returncode
            except subprocess.TimeoutExpired:
                stream.write('\nrunner: stopped this suite after 180 seconds.\n')
                returncode = 124
        raw = logfile.read_text(encoding='utf-8', errors='replace')
        found = re.findall(r'Ran (\d+) tests? in', raw)
        actual = int(found[-1]) if found else None
        passed = returncode == 0 and (expected is None or actual == expected)
        item = {'name': name, 'mode': mode, 'passed': passed,
                'exit_code': returncode, 'tests_expected': expected,
                'tests_run': actual,
                'seconds': round(time.monotonic() - started, 3),
                'log': logfile.relative_to(output).as_posix()}
        summary['suites'].append(item)
        print(f'  {"pass" if passed else "FAIL"}: {item["log"]}', flush=True)
        (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    summary['project_unchanged_during_checks'] = before == inventory(project)
    summary['unit_tests_run'] = sum(
        item['tests_run'] or 0 for item in summary['suites'])
    summary['all_passed'] = all(item['passed'] for item in summary['suites'])
    summary['all_passed'] &= summary['project_unchanged_during_checks']
    summary['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for filename, key in [('interface/interface_report.json', 'interface'),
                          ('compatibility.json', 'compatibility'),
                          ('playthroughs.json', 'playthroughs'),
                          ('real_audio.json', 'real_audio'),
                          ('template_preservation.json', 'template_preservation'),
                          ('submission_audit.json', 'submission_audit')]:
        report = output / filename
        if report.exists():
            summary[key] = json.loads(report.read_text())
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(f'\n{"pass" if summary["all_passed"] else "FAIL"}: '
          f'{summary["unit_tests_run"]} unit tests; see {output / "summary.json"}')
    return 0 if summary['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())


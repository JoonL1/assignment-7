"""check that a game zip contains exactly the files tied to this evidence."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import stat
import zipfile


def main():
    """compare every archived file, then save a separate archive proof."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--evidence', type=Path,
                        default=Path(__file__).resolve().parent / 'evidence')
    options = parser.parse_args()
    archive = options.archive.expanduser().resolve()
    evidence = options.evidence.expanduser().resolve()
    summary_path = evidence / 'summary.json'
    summary_bytes = summary_path.read_bytes()
    summary = json.loads(summary_bytes)
    expected = summary['project_files']
    issues = []
    if not summary.get('all_passed'):
        issues.append('the associated runtime check run did not fully pass')
    seen = set()
    verified = 0
    with zipfile.ZipFile(archive) as zipped:
        for info in zipped.infolist():
            if info.is_dir():
                continue
            name = info.filename
            if name in seen:
                issues.append('duplicate archive path: ' + name)
            seen.add(name)
            if not name.startswith('shield/'):
                issues.append('file is outside the shield folder: ' + name)
                continue
            relative = name[len('shield/'):]
            if relative not in expected:
                issues.append('unexpected archive file: ' + name)
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                issues.append('symlink in archive: ' + name)
                continue
            data = zipped.read(info)
            wanted = expected[relative]
            if len(data) != wanted['bytes']:
                issues.append('size mismatch: ' + name)
            elif hashlib.sha256(data).hexdigest() != wanted['sha256']:
                issues.append('content hash mismatch: ' + name)
            else:
                verified += 1
    for relative in expected:
        if 'shield/' + relative not in seen:
            issues.append('missing archive file: shield/' + relative)
    report = {
        'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'archive_filename': archive.name,
        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'archive_bytes': archive.stat().st_size,
        'summary_sha256': hashlib.sha256(summary_bytes).hexdigest(),
        'expected_files': len(expected),
        'verified_files': verified,
        'passed': not issues,
        'issues': issues,
    }
    (evidence / 'archive_verification.json').write_text(
        json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

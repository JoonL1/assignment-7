"""check exactly the supplied template text and preserve the filled code."""
import ast
import json

from qa_paths import BUNDLE, OUTPUT, PROJECT
from template_tools import comments, documentation, executable_signatures
from template_tools import digest, method_blocks, named_nodes


manifest = json.loads((BUNDLE / 'template_preservation_manifest.json').read_text())
issues = []
results = []
for filename, reference in manifest['modules'].items():
    text = (PROJECT / filename).read_text()
    actual_docs = documentation(text)
    for owner, expected in reference['template_documentation'].items():
        if actual_docs.get(owner) != expected['expected_raw']:
            issues.append(f'{filename}: original documentation changed: {owner}')
    for owner, expected in reference['added_documentation'].items():
        if actual_docs.get(owner) != expected:
            issues.append(f'{filename}: added documentation changed: {owner}')
    actual_methods = method_blocks(text)
    for owner, expected in reference['added_method_blocks'].items():
        if actual_methods.get(owner) != expected:
            issues.append(f'{filename}: added method block changed: {owner}')
    signatures = executable_signatures(text)
    if signatures != reference['baseline_executable_signatures']:
        issues.append(f'{filename}: executable tokens or ast changed')

    current_comments = comments(text)
    cursors = {}
    preserved_comments = []
    nodes = named_nodes(text)
    for expected in reference['template_comments']:
        scope = expected['scope']
        candidates = [item for item in current_comments if item['scope'] == scope]
        start = cursors.get(scope, 0)
        match = next((index for index in range(start, len(candidates))
                      if candidates[index]['text'] == expected['text']), None)
        if match is None:
            issues.append(f'{filename}: missing/reordered comment in {scope}: '
                          + expected['text'])
            continue
        observed = candidates[match]
        cursors[scope] = match + 1
        for field, value in expected['placement'].items():
            if field == 'before_implementation':
                node = nodes[scope]
                statements = node.body[1:]
                if not statements or observed['line'] >= statements[0].lineno:
                    issues.append(f'{filename}: implementation marker moved in {scope}')
            elif observed[field] != value:
                issues.append(f'{filename}:{observed["line"]}: comment placement '
                              f'changed ({field}) in {scope}: {expected["text"]}')
        preserved_comments.append({'text': observed['text'], 'scope': scope,
                                   'original_line': expected['line'],
                                   'current_line': observed['line']})
    results.append({
        'file': filename, 'sha256': digest(text),
        'template_documentation_blocks': len(reference['template_documentation']),
        'template_comment_tokens': len(reference['template_comments']),
        'added_method_blocks_unchanged': len(reference['added_method_blocks']),
        'executable_signatures': signatures,
        'preserved_comments': preserved_comments,
        'metadata_replacements': reference['metadata_replacements'],
    })

report = {
    'source_archive': manifest['source_archive'],
    'source_archive_sha256': manifest['source_archive_sha256'],
    'template_documentation_blocks': sum(x['template_documentation_blocks'] for x in results),
    'template_comment_tokens': sum(x['template_comment_tokens'] for x in results),
    'added_method_blocks_unchanged': sum(x['added_method_blocks_unchanged'] for x in results),
    'allowed_changes': 'only the two module-header placeholders use existing metadata',
    'new_template_resources_match_previous_starter': manifest['resource_comparison'],
    'files': results, 'issues': issues, 'passed': not issues,
}
(OUTPUT / 'template_preservation.json').write_text(json.dumps(report, indent=2) + '\n')
print('original documentation blocks:', report['template_documentation_blocks'])
print('original comment tokens:', report['template_comment_tokens'])
print('unchanged added method blocks:', report['added_method_blocks_unchanged'])
if issues:
    print('\n'.join(issues))
    raise SystemExit(1)
print('pass: exact template text, section placement, added helpers, and filled code')

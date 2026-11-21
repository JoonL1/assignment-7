"""check style, protected starter files, and all original assets."""
import ast
from pathlib import Path
import hashlib
import json


from qa_paths import BUNDLE, OUTPUT, PROJECT
issues = []
methods = []
template = json.loads((BUNDLE / "template_preservation_manifest.json").read_text())
width_exemptions = []
used_exemptions = set()

for filename in ["app.py", "wave.py", "models.py", "consts.py"]:
    path = PROJECT / filename
    text = path.read_text()
    lines = text.splitlines()
    tree = ast.parse(text, filename=filename)
    for number, line in enumerate(lines, 1):
        if "\t" in line:
            issues.append(f"{filename}:{number}: tab character")
        if len(line) > 80:
            original = next((entry for entry in template["original_width_exemptions"]
                             if entry["file"] == filename and entry["text"] == line
                             and (filename, entry["original_line"]) not in used_exemptions), None)
            if original is None:
                issues.append(f"{filename}:{number}: {len(line)} characters")
            else:
                used_exemptions.add((filename, original["original_line"]))
                width_exemptions.append({**original, "current_line": number,
                                         "reason": "verbatim original template line"})
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                issues.append(f"{filename}:{node.lineno}: missing method spec")
            body_start = node.body[0].lineno
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    body_start = first.end_lineno + 1
            body = lines[body_start - 1:node.end_lineno]
            count = sum(bool(line.strip()) for line in body)
            methods.append((count, filename, node.name))
            if count > 25:
                issues.append(f"{filename}:{node.lineno}: {node.name} has {count} body lines")

reference = json.loads((BUNDLE / "starter_manifest.json").read_text())
checked_originals = 0
checked_assets = 0
for group in ["protected_files", "asset_files"]:
    for relative, expected in reference[group].items():
        path = PROJECT / relative
        if group == "protected_files":
            checked_originals += 1
        else:
            checked_assets += 1
        if not path.exists():
            issues.append(f"Required original missing: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
            issues.append(f"Required original changed: {relative}")

report = {"method_count": len(methods),
          "protected_originals_checked": checked_originals,
          "original_assets_checked": checked_assets,
          "largest_method_body": max(count for count, _, _ in methods),
          "original_width_exemptions": width_exemptions,
          "methods": [{"body_lines": count, "file": file, "name": name}
                      for count, file, name in methods],
          "issues": issues}
(OUTPUT / "submission_audit.json").write_text(json.dumps(report, indent=2) + "\n")

print(f"Audited {len(methods)} methods and {checked_originals} protected originals.")
print(f"Also checked {checked_assets} original font/image/sound assets.")
for entry in width_exemptions:
    print(f"Original width exemption: {entry['file']}:{entry['current_line']} "
          f"({entry['characters']} chars; template line {entry['original_line']})")
print("Largest methods:")
for count, filename, name in sorted(methods, reverse=True)[:8]:
    print(f"  {count}: {filename}:{name}")
if issues:
    print("ISSUES:")
    for issue in issues:
        print("  " + issue)
    raise SystemExit(1)
print("PASS: method lengths, line lengths, docstrings, tabs, protected originals")

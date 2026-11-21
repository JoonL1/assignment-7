"""compile every python file in memory, so the game folder stays clean."""
from qa_paths import PROJECT


paths = sorted(PROJECT.rglob('*.py'))
for path in paths:
    compile(path.read_bytes(), str(path), 'exec')
print(f'pass: compiled {len(paths)} python files without writing bytecode')


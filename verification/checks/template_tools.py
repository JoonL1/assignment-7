"""small source readers for the exact template-preservation check."""
import ast
import hashlib
import io
import json
import tokenize


def digest(text):
    """hash utf-8 text without changing its spaces or line endings."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def named_nodes(text):
    """name the module, classes, and methods so moving lines is harmless."""
    tree = ast.parse(text)
    found = {'<module>': tree}

    def visit(parent, prefix):
        for node in parent.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                name = prefix + node.name
                found[name] = node
                visit(node, name + '.')

    visit(tree, '')
    return found


def documentation(text):
    """read raw docstring literals, including the standalone cli explanation."""
    found = {}
    for name, node in named_nodes(text).items():
        if node.body and isinstance(node.body[0], ast.Expr):
            value = node.body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                found[name] = ast.get_source_segment(text, node.body[0])
        extra = 0
        for statement in node.body[1:]:
            if isinstance(statement, ast.Expr):
                value = statement.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    extra += 1
                    found[f'{name}:text:{extra}'] = ast.get_source_segment(
                        text, statement)
    return found


def executable_signatures(text):
    """ignore documentation/comments, but retain executable tokens and ast."""
    tree = ast.parse(text)
    spans = [(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
             for node in ast.walk(tree)
             if isinstance(node, ast.Expr)
             and isinstance(node.value, ast.Constant)
             and isinstance(node.value.value, str)]

    class WithoutDocumentation(ast.NodeTransformer):
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    return None
            return self.generic_visit(node)

    stripped = WithoutDocumentation().visit(tree)
    ast_hash = digest(ast.dump(stripped, include_attributes=False))
    ignored = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
               tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER,
               tokenize.ENCODING}
    kept = []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type in ignored:
            continue
        if any((a, b) <= token.start and token.end <= (c, d)
               for a, b, c, d in spans):
            continue
        kept.append((token.type, token.string))
    return {'ast_sha256': ast_hash,
            'token_sha256': digest(json.dumps(kept, ensure_ascii=False))}


def method_blocks(text):
    """hash whole method blocks, so helper specs and code must both stay put."""
    return {name: digest(ast.get_source_segment(text, node))
            for name, node in named_nodes(text).items()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def statement_name(node):
    """describe a top-level statement without depending on its line number."""
    if isinstance(node, ast.Assign):
        return 'assign:' + ','.join(ast.unparse(target) for target in node.targets)
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return type(node).__name__ + ':' + node.name
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
        if isinstance(node.value.value, str):
            return 'text:' + digest(node.value.value)
    return type(node).__name__


def comments(text):
    """keep exact comment tokens, their scope, and the next member/statement."""
    tree = ast.parse(text)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    found = []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        row, column = token.start
        scope = '<module>'
        member = None
        owner = None
        for index, node in enumerate(classes):
            end = classes[index + 1].lineno if index + 1 < len(classes) else float('inf')
            if node.lineno <= row < end and column >= node.col_offset + 4:
                owner = node
                scope = node.name
                break
        if owner is not None:
            methods = [node for node in owner.body
                       if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
            for index, method in enumerate(methods):
                end = methods[index + 1].lineno if index + 1 < len(methods) else float('inf')
                if (method.lineno <= row < end
                        and column >= method.col_offset + 4):
                    scope += '.' + method.name
                    break
            if scope == owner.name:
                member = next((node.name for node in methods if node.lineno > row), None)
        next_statement = next((statement_name(node) for node in tree.body
                               if node.lineno > row), None)
        prefix = token.line[:column].strip()
        found.append({'text': token.string, 'scope': scope,
                      'line': row, 'column': column,
                      'next_member': member, 'next_statement': next_statement,
                      'inline_prefix': prefix})
    return found


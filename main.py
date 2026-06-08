import re


class JinjaRenderError(Exception):
    pass


def _resolve(expr, local_symbols):
    """Follow a dotted name (e.g. 'product.price') through dicts/objects."""
    parts = expr.split(".")
    val = local_symbols.get(parts[0])
    for part in parts[1:]:
        if val is None:
            break
        val = val.get(part) if isinstance(val, dict) else getattr(val, part, None)
    return val


def _diagnose(exc):
    # Walk the full chain and keep updating — the deepest .html/.j2 frame is
    # where the crash actually occurred (handles includes, macros, etc.).
    jinja_frame = jinja_lineno = None

    tb = exc.__traceback__
    while tb:
        if tb.tb_frame.f_code.co_filename.endswith((".html", ".j2")):
            jinja_frame = tb.tb_frame
            jinja_lineno = tb.tb_lineno
        tb = tb.tb_next

    if not jinja_frame:
        return None

    local_symbols = jinja_frame.f_locals
    failing_line = ""

    try:
        with open(jinja_frame.f_code.co_filename) as f:
            lines = f.readlines()
        failing_line = lines[jinja_lineno - 1] if jinja_lineno else ""
    except OSError:
        pass

    missing_iterables = []
    for m in re.finditer(r"\bin\s+(\w+)", failing_line):
        var_name = m.group(1)
        if var_name in local_symbols and local_symbols[var_name] is None:
            missing_iterables.append(var_name)

    filter_suspects = []
    if not missing_iterables:
        for m in re.finditer(r"\{\{-?\s*([\w.]+)\s*\|\s*(\w+)", failing_line):
            expr, filter_name = m.group(1), m.group(2)
            val = _resolve(expr, local_symbols)
            if val is not None or expr.split(".")[0] in local_symbols:
                filter_suspects.append((expr, filter_name, val))

    out = ["=" * 60, f"JINJA RENDER ERROR: {exc}", "=" * 60]

    if missing_iterables:
        out.append(f"SUSPECT VARIABLES (None): {missing_iterables}")
        out.append(f"  Look for '... in {missing_iterables[0]}' in your template.")

    if filter_suspects:
        out.append("FILTER TYPE MISMATCH:")
        for expr, filter_name, val in filter_suspects:
            out.append(f"  '{filter_name}' received {type(val).__name__} for '{expr}'")

    out.append("\nTEMPLATE INPUT DATA:")
    for var in missing_iterables:
        out.append(f"  {var} = {local_symbols.get(var, 'NOT PASSED TO TEMPLATE')}")
    for expr, _, val in filter_suspects:
        out.append(f"  {expr} = {val!r}")

    out.append("=" * 60)
    return "\n".join(out)


def render(template, **context):
    """Render a Jinja2 template, raising JinjaRenderError with diagnostics on failure."""
    try:
        return template.render(**context)
    except Exception as exc:
        diagnostic = _diagnose(exc)
        if diagnostic:
            raise JinjaRenderError(diagnostic) from exc
        raise

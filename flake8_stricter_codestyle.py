import tokenize

from flake8.processor import expand_indent

name = "flake8-stricter-codestyle"
__version__ = "0.0.1"


VALID_HANG_SPACES = (4,)
PLUGIN_PREFIX = 'STR'


def backslash_continuation(physical_line):
    """Backslash continuations are strongly discouraged."""
    stripped = physical_line.rstrip('\r\n')
    if stripped.endswith('\\'):
        return len(stripped), f"{PLUGIN_PREFIX}201 backslash continuation"


def continued_indentation(logical_line, tokens, indent_level, hang_closing, noqa):
    """Continuation lines indentation.

    Continuation lines should use Python's implicit line joining and a
    hanging indent.

    When using a hanging indent these considerations should be applied:
    - there should be no arguments on the first line, and
    - further indentation should be used to clearly distinguish itself
      as a continuation line.
    """
    first_row = tokens[0][2][0]
    nrows = 1 + tokens[-1][2][0] - first_row
    if noqa or nrows == 1:
        return

    # indent_next tells us whether the next block is indented; assuming
    # that it is indented by 4 spaces, then we should not allow 4-space
    # indents on the final continuation line; in turn, some other
    # indents are allowed to have an extra 4 spaces.
    indent_next = logical_line.endswith(':')

    row = depth = 0
    # remember how many brackets were opened on each line
    parens = [0] * nrows
    # relative indents of physical lines
    rel_indent = [0] * nrows
    # for each depth, collect a list of opening rows
    open_rows = [[0]]
    # for each depth, memorize the hanging indentation
    hangs = [None]

    for token_type, text, start, end, line in tokens:

        newline = row < start[0] - first_row
        if newline:
            row = start[0] - first_row
            newline = token_type not in (tokenize.NL, tokenize.NEWLINE)

        if newline:
            # this is the beginning of a continuation line.

            # record the initial indent.
            rel_indent[row] = expand_indent(line) - indent_level

            # identify closing bracket
            close_bracket = (token_type == tokenize.OP and text in ']})')

            # is the indent relative to an opening bracket line?
            for open_row in reversed(open_rows[depth]):
                hang = rel_indent[row] - rel_indent[open_row]
                hanging_indent = hang in VALID_HANG_SPACES
                if hanging_indent:
                    break

            if hangs[depth]:
                hanging_indent = (hang == hangs[depth])

            if close_bracket and not hang:
                # closing bracket matches indentation of opening
                # bracket's line
                if hang_closing:
                    yield start, f"{PLUGIN_PREFIX}133 closing bracket is missing indentation"
            elif hanging_indent or (indent_next and rel_indent[row] == 8):
                # hanging indent is verified
                if close_bracket and not hang_closing:
                    yield (
                        start,
                        f"{PLUGIN_PREFIX}123 closing bracket does not match indentation of "
                        "opening bracket's line",
                    )
                hangs[depth] = hang
            else:
                # indent is broken
                if hang <= 0:
                    error = f"{PLUGIN_PREFIX}122", "missing indentation or outdented"
                elif not close_bracket and hangs[depth]:
                    error = f"{PLUGIN_PREFIX}131", "unaligned for hanging indent"
                else:
                    hangs[depth] = hang
                    if hang > 4:
                        error = f"{PLUGIN_PREFIX}126", "over-indented for hanging indent"
                    else:
                        error = f"{PLUGIN_PREFIX}121", "under-indented for hanging indent"
                yield start, "%s continuation line %s" % error

        if text == ':' and line[end[1]:].isspace():
            open_rows[depth].append(row)

        # keep track of bracket depth
        if token_type == tokenize.OP:
            if text in '([{':
                depth += 1
                hangs.append(None)
                if len(open_rows) == depth:
                    open_rows.append([])
                open_rows[depth].append(row)
                parens[row] += 1
            elif text in ')]}' and depth > 0:
                # parent indents should not be more than this one
                hangs.pop()
                del open_rows[depth + 1:]
                depth -= 1
                for idx in range(row, -1, -1):
                    if parens[idx]:
                        parens[idx] -= 1
                        break

    if indent_next and expand_indent(line) == indent_level + 4:
        pos = (start[0], indent_next)
        yield pos, "E125 continuation line with same indent as next logical line"

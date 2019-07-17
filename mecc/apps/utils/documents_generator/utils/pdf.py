import html
import re


def filter_content(content):
    """
    Content passed to reportlab should be filtered for special cases, this
    function is intended to be a central place where it can be filtered
    """
    # Tags must be closed : eg <br>
    content = content.replace('<br>', '<br/>')

    # Escape &, for example in R&D
    content = re.sub(r"&(?!amp;)", "&amp;", html.unescape(content))

    return content

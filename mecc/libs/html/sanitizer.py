from html_sanitizer.django import get_sanitizer


def sanitize(bad):
    """
    Clean html string by removing all tags which are not in a whitelist

    :param bad: html to clean
    :return: cleaned html
    :rtype: str
    """
    sanitizer = get_sanitizer(name='rules')
    good = sanitizer.sanitize(bad)

    return good

import bleach


allowed_tags = [
    'abbr', 'acronym',
    'b', 'br',
    'em',
    'i',
    'li',
    'ol',
    'p',
    'strong',
    'u', 'ul',
]


def sanitize(bad):
    """
    Clean html string by removing all tags which are not in a whitelist

    :param bad: html to clean
    :return: cleaned html
    :rtype: str
    """
    good = bleach.clean(
        bad,
        tags=allowed_tags,
        strip=True,
        strip_comments=True
    )

    return good

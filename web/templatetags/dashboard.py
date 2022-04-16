from django import template

register = template.Library()


@register.simple_tag
def used_space(size):
    if size >= 1024 * 1024 * 1024:  # G
        return "%.2fG" % (size / (1024 * 1024 * 1024))
    elif size >= 1024 * 1024:  # M
        return "%.2fM" % (size / (1024 * 1024))
    elif size >= 1024:  # K
        return "%.2fK" % (size / 1024)
    else:
        return "%dB" % size

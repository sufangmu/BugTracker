from django import template

register = template.Library()


@register.simple_tag
def string_zfill(num):
    return "#{}".format(str(num).zfill(3))

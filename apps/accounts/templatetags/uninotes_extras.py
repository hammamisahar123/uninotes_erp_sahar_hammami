from django import template

register = template.Library()

@register.filter
def dict_key(d, k):
    return d.get(k, '')

@register.filter
def split(value, sep):
    return value.split(sep)

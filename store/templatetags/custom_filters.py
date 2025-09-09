from django import template
from store.models import Spec

register = template.Library()

@register.filter
def get_spec_by_name(spec_name):
    return Spec.objects.get(name=spec_name)

@register.filter
def get_range(start, end):
    try:
        return range(int(start), int(end) + 1)
    except (ValueError, TypeError):
        return []

@register.filter
def get_item(dictionary, key):
    return dictionary.get(int(key), 0)

@register.filter
def split(value, separator):
    if not isinstance(value, str):
        return value
    return value.split(separator)

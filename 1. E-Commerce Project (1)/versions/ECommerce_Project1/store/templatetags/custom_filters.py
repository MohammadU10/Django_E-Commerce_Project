from django import template
from store.models import Spec

register = template.Library()

@register.filter
def get_spec_by_name(spec_name):
    return Spec.objects.get(name=spec_name)

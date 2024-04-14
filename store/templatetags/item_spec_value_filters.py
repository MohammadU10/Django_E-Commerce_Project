from django import template

register = template.Library()

from store.models import ItemSpecValue, Spec

@register.filter
def get_item_spec_values_for_spec(item_spec_values, spec_name):
    try:
        spec = Spec.objects.get(name=spec_name)
        return item_spec_values.filter(spec=spec)
    except Spec.DoesNotExist:
        return ItemSpecValue.objects.none()

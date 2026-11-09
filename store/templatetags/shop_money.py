from django import template
from store.money import format_inr

register = template.Library()


@register.filter(name="inr")
def inr(value):
    return format_inr(value)

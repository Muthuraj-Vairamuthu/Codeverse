from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter"""
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter)]

@register.filter
def trim(value):
    """Trim whitespace from string"""
    if not value:
        return value
    return value.strip()

@register.filter  
def cut(value, arg):
    """Remove all instances of arg from value"""
    if not value:
        return value
    return value.replace(arg, '')

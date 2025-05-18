from django import template

register = template.Library()

@register.filter(name='split')
def split(value, separator=','):
   
    if not isinstance(value, str):
        return []
    return value.split(separator)

@register.filter(name='trim')
def trim(value):
    
    if isinstance(value, str):
        return value.strip()
    return ''
def zip(a, b):
    return zip(a, b)
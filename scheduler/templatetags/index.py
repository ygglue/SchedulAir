from django import template
register = template.Library()

@register.filter
def index(list_obj, i):
    try:
        return list_obj[int(i)]
    except:
        return ''

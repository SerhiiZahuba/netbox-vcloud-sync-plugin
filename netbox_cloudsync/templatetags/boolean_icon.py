from django import template
register = template.Library()

@register.filter()
def boolean_icon(value):

    if value:
        return '<span class="text-success"><i class="mdi mdi-check-bold"></i></span>'
    else:
        return '<span class="text-danger"><i class="mdi mdi-close-thick"></i></span>'

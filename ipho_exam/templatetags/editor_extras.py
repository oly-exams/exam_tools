from django.template.defaulttags import register


@register.filter(name="lookup")
def lookup(value, arg):
    return value[arg]


@register.filter(name="get")
def get(value, arg):
    return value.get(arg)

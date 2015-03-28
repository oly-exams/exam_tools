from django.template.defaulttags import register

@register.filter(name='lookup')
def lookup(value, arg):
    print value[arg]
    return value[arg]


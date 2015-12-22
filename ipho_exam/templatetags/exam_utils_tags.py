from django.template.defaulttags import register

@register.filter(name='intlist')
def to_intlist(raw_list):
    return [int(li) for li in raw_list]

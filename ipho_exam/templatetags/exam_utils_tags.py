from django.template.defaulttags import register

@register.filter(name='intlist')
def to_intlist(raw_list):
    return [int(li) for li in raw_list]

@register.simple_tag(takes_context=True)
def this_url(context, **kwargs):
    func = context['this_url_builder']
    return func(**kwargs)

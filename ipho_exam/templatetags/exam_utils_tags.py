from django.template.defaulttags import register


@register.filter(name="intlist")
def to_intlist(raw_list):
    return [int(li) for li in raw_list]


@register.filter
def has_scan_file(docs_list):
    return any(doc.scan_file for doc in docs_list)


@register.filter
def binand(value, arg):
    return value & arg


@register.simple_tag(takes_context=True)
def this_url(context, **kwargs):
    func = context["this_url_builder"]
    return func(**kwargs)

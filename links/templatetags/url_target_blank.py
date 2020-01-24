from django.template.defaulttags import register

def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')
    # return re.sub("<a([^>]+)(?<!target=)>",'<a target="_blank"\\1>',text) # this is more accurate, but 10X slower than replace (benchmarked)
url_target_blank = register.filter(url_target_blank, is_safe = True)
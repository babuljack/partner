from django import template
import re
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from Account.models import User
from django.utils.html import escape
register = template.Library()

#tag_content
def generate_link(link):
    return '<a class="link" target="_blank" href="{}">{}</a>'.format(link, link)

def generate_hashtag_link(tag):
    url = "/tags/{}".format(tag)
    return '<a class="hashtag"  href="{}">#{}</a>'.format(url, tag)

def mention_link(value):
    try:
        user=User.objects.get(username=value)
        url = "/user/{}".format(user)
        return '<a class="hashtag" style="font-size:16px;font-weight:bold;color:red;padding:5px" href="{}">{}</a>'.format(url, user)
    except:
        return '<span>@{}</span>'.format(value)  


@register.filter  
def content(obj):
    task=escape(obj)
    has=re.sub(r"#(\w+)", lambda m: generate_hashtag_link(m.group(1)),task)
    link=re.sub(r"(?P<url>https?://[^\s]+)",lambda m: generate_link(m.group(1)),has)
    mention=re.sub(r"@(\w+)", lambda m: mention_link(m.group(1)),link)
    return mark_safe(mention)
    


'''#mention
def mention_link(value):
    try:
        user=User.objects.get(username=value)
        url = "/user/{}".format(user)
        return '<a class="hashtag" style="font-size:16px;font-weight:bold;color:red;padding:5px" href="{}">{}</a>'.format(url, user)
    except:
        return '<span>@{}</span>'.format(value)    

@register.filter
def mention(obj): 
    task=escape(obj) 
    text = re.sub(r"@(\w+)", lambda m: mention_link(m.group(1)),task)
    return mark_safe(text)'''






#wordcutting

@register.filter
def wordcutter(value,max_length):
    print(max_length)
    if len(value) > max_length:
        truncd_val = value[:max_length]
        if not len(value) == max_length+1 and value[max_length+1] != " ":
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
            url='hello man'
            link=f'<a href="{url}">See More</a> '
            trunced=mark_safe(truncd_val + '...'+link)
        return trunced
    return value


from django import template

register = template.Library()

@register.filter
def reading_time(text):
    words = len(text.split())
    return max(1, words // 200)
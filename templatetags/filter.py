from django import template
register = template.Library()

@register.filter("mongo_id")
def mongo_id(value):
    return str(value['_id'])

register.filter('mongo_id', mongo_id)

@register.filter("times")
def times(number):
    return range(number)
register.filter('times', times)
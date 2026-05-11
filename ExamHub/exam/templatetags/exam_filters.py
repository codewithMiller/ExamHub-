from django import template

register = template.Library()

@register.filter
def options_list(question):
    return [
        ('A', question.option_a),
        ('B', question.option_b),
        ('C', question.option_c),
        ('D', question.option_d),
    ]
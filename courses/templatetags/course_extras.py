import markdown2
from django import template
from django.utils.safestring import mark_safe

from courses.models import Course

register = template.Library()


@register.simple_tag
def newest_course():
    """this gives the newest course available"""
    return Course.objects.filter(published=True).latest("created_at")
    # register.simple_tag('newest_course')


@register.inclusion_tag('courses/course_nav.html')
def nav_course_list():
    # usign this inclusion tag this gives us the template we
    # its on us to include this into any other template or not
    """this gives the list of the courses availbale """
    courses = Course.objects.filter(
        published=True
    ).order_by(
        # -created_at - sign is for descending order_by
        '-created_at'
    ).values(
        'id', 'title'
    ).all()
    # fetching  out only those fields which are needed as on nav_course_
    return {'courses': courses}
    # @register.inclusion_tag('courses/course_nav.html')(nav_course_list)


@register.filter('time_estimate')
def time_estimate(word_count):
    """this is the estimate time taken to complete the step"""
    # actually this is the filter used with |
    minutes = round(word_count / 10)
    return minutes


@register.filter('markdown_to_html')
def markdown_to_html(markdown_text):
    """this coverts the markdown text into html body"""
    html_body = markdown2.markdown(markdown_text)
    return mark_safe(html_body)


@register.filter('total_steps')
def total_steps(steps):
    count = 0
    for step in steps:
        count += 1
    if count == 1:
        return 'is'
    else:
        return 'are'

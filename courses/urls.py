from django.conf.urls import url
from . import views

urlpatterns = [
    # as chevron is missd in the ok field as it can't be
    # start from the pk or id
    url(r'^$', views.course_list, name='list'),
    url(r'(?P<course_pk>\d+)/t(?P<step_pk>\d+)/$', views.text_detail, name='text'),
    url(r'(?P<course_pk>\d+)/q(?P<step_pk>\d+)/$', views.quiz_detail, name='quiz'),
    url(r'(?P<course_pk>\d+)/create_quiz/$', views.create_quiz, name='create_quiz'),
    url(r'(?P<course_pk>\d+)/edit_quiz/(?P<quiz_pk>\d+)/$', views.quiz_edit, name='quiz_edit'),
    url(r'(?P<quiz_pk>\d+)/create_question/(?P<question_type>mc|tf)/$', views.create_question, name='create_question'),
    url(r'(?P<quiz_pk>\d+)/edit_question/(?P<question_pk>\d+)/$', views.edit_question, name='edit_question'),
    url(r'(?P<question_pk>\d+)/create_answer/$', views.answer_form, name='create_answer'),
    url(r'by/(?P<teacher_name>[_\w]+)/$', views.course_by_teacher, name='by_teacher'),
    url(r'search/$', views.search, name='search'),
    url(r'(?P<pk>\d+)/$', views.course_detail, name='detail'),

]

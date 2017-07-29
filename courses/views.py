from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from . import forms
from . import models
from .forms import AnswerInlineFormSet

email = "question@learning_site.com"


def course_list(request):
    courses = models.Course.objects.filter(
        published=True
    ).annotate(
        total_steps=Count('text', distinct=True) + Count('quiz', distinct=True)
    )
    total = courses.aggregate(total=Sum('total_steps'))

    # output  = ", ".join([str(course) for course in courses])
    # return HttpResponse(output)
    return render(request, 'courses/course_list.html', {'courses': courses,
                                                        'email': email,
                                                        'total': total})


# we will provide the pk through url

def course_detail(request, pk):
    try:
        course = models.Course.objects.prefetch_related(
            'quiz_set', 'text_set', 'quiz_set__question_set'
            # fetching out the quiz_set and text_set and then fetching out the question_set
        ).get(pk=pk, published=True)
    except models.Course.DoesNotExist:
        raise Http404
    else:
        # as we didn't d efine the pk a django knows that our primary key ie. pk default is the id
        # course = models.Course.objects.get(pk=pk)
        # course = get_object_or_404(models.Course,
        #                            pk=pk,
        #                            published=True)
        # sort all the combination sof the iterable swhich are all the set of Step to Course
        steps = sorted(chain(
            course.text_set.all(),
            course.quiz_set.all()
        ), key=lambda step: step.order)
    return render(request,
                  'courses/course_detail.html',
                  {'course': course,
                   'steps': steps,
                   })


def text_detail(request, course_pk, step_pk):
    step = get_object_or_404(models.Text,
                             course_id=course_pk,
                             pk=step_pk,
                             course__published=True)
    # course_id is the for<link rel="stylesheet" href="{% static 'courses/css/courses.css' %}">eign key field{}
    return render(request, 'courses/text_detail.html', {'step': step})


def quiz_detail(request, course_pk, step_pk):
    try:
        step = models.Quiz.objects.select_related(
            'course'
        ).prefetch_related(
            'question_set',
            'question_set__answer_set',
        ).get(course_id=course_pk,
              pk=step_pk,
              course__published=True)
    except models.Quiz.DoesNotExist:
        raise Http404
    else:
        # step = get_object_or_404(models.Quiz,
        #                          course_id=course_pk,
        #                          pk=step_pk,
        #                          course__published=True)
        # course_id is the foreign key field{}
        return render(request, 'courses/quiz_detail.html', {'step': step})


# making a view for creating a  quiz
@login_required
def create_quiz(request, course_pk):
    course = get_object_or_404(models.Course,
                               pk=course_pk,
                               published=True)
    # associating the quiz with the course

    form = forms.QuizForm()
    # making instance of Quiz form
    if request.method == 'POST':
        form = forms.QuizForm(request.POST)
        # if request is  pOst then  put the data into form
        if form.is_valid():
            quiz = form.save(commit=False)
            # generally we commit True as we say hold the form with data we have to
            # associate it with the course add some info
            quiz.course = course
            quiz.save()
            messages.add_message(request, messages.SUCCESS, "Quiz added!!")
            return HttpResponseRedirect(quiz.get_absolute_url())

    return render(request, 'courses/quiz_form.html', {'form': form, 'course': course})


# creating a view to edit the quiz

@login_required
def quiz_edit(request, course_pk, quiz_pk):
    quiz = get_object_or_404(models.Quiz,
                             pk=quiz_pk,
                             course_id=course_pk,
                             course__published=True)
    # putting this quiz instance which we have clicked on
    form = forms.QuizForm(instance=quiz)

    if request.method == "POST":
        # request.POST returns mutable dict
        form = forms.QuizForm(instance=quiz, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated {}.".format(form.cleaned_data['title']))
            return HttpResponseRedirect(quiz.get_absolute_url())

    return render(request, 'courses/quiz_form.html', {'form': form, 'course': quiz.course})
    # quiz.course come from the model Quiz as fk course defined


# making view for creating a question
@login_required
def create_question(request, quiz_pk, question_type):
    quiz = get_object_or_404(models.Quiz, pk=quiz_pk)
    if question_type == 'tf':
        form_class = forms.TrueFalseQuestionForm
    else:
        form_class = forms.MultipleChoiceQuestionForm

    # instatiating after getting to know which form are we taking
    form = form_class()
    # here we are using the Imlineformset for the answers
    answer_forms = AnswerInlineFormSet(
        queryset=models.Answer.objects.none()
    )
    # as we are creating new question so no new answers should be ther so we only  display none

    if request.method == 'POST':
        form = form_class(request.POST)
        answer_forms = AnswerInlineFormSet(
            request.POST,
            queryset=models.Answer.objects.none()
        )

        if form.is_valid() and answer_forms.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            answers = answer_forms.save(commit=False)
            for answer in answers:
                # linking answer with question
                answer.question = question
                answer.save()

            messages.success(request, "Question Added!!")
            return HttpResponseRedirect(quiz.get_absolute_url())

    return render(request, 'courses/question_form.html', {'form': form,
                                                          'quiz': quiz,
                                                          'formset': answer_forms
                                                          })


@login_required
def edit_question(request, quiz_pk, question_pk):
    question = get_object_or_404(models.Question, pk=question_pk, quiz_id=quiz_pk)
    # we are checking the question object is having an attribute according
    # to that we take the form editing
    if hasattr(question, 'truefalsequestion'):
        form_class = forms.TrueFalseQuestionForm
        question = question.truefalsequestion

    else:
        form_class = forms.MultipleChoiceQuestionForm
        question = question.multiplechoicequestion

    form = form_class(instance=question)
    answer_forms = AnswerInlineFormSet(
        queryset=form.instance.answer_set.all()
    )

    if request.method == 'POST':
        # here we used different approach to push the data into form as data= request.POST
        form = form_class(request.POST, instance=question)
        answer_forms = AnswerInlineFormSet(
            request.POST,
            queryset=form.instance.answer_set.all()
        )
        if form.is_valid() and answer_forms.is_valid():
            form.save()
            # we can do answer_forms.save() but new answers being filled out sowe do another method
            answers = answer_forms.save(commit=False)
            for answer in answers:
                answer.question = question
                answer.save()
            for answer in answer_forms.deleted_objects:
                answer.delete()

            messages.success(request, 'Updated Question')
            return HttpResponseRedirect(question.quiz.get_absolute_url())

    return render(request, 'courses/question_form.html', {'form': form,
                                                          'quiz': question.quiz,
                                                          'formset': answer_forms})


@login_required
def answer_form(request, question_pk, answer_pk=None):
    question = get_object_or_404(models.Question, pk=question_pk)
    # form = forms.AnswerForm()
    # using the Answerformset
    formset = forms.AnswerFormSet(queryset=question.answer_set.all())
    # not editing single answers
    # if answer_pk:
    #     answer = get_object_or_404(models.Answer, pk=answer_pk)
    #     form = forms.AnswerForm(instance=answer)
    if request.method == 'POST':
        # if answer_pk:
        #     form = forms.AnswerForm(request.POST, instance=answer)
        # else:
        #     form = forms.AnswerForm(request.POST)
        # if form.is_valid():
        # answer.question is accessed from the models through forms
        # answer = form.save(commit=False)
        # answer.question = question
        # answer.save()
        # return HttpResponseRedirect(question.get_absolute_url())
        formset = forms.AnswerFormSet(request.POST,
                                      queryset=question.answer_set.all())

        if formset.is_valid():
            answers = formset.save(commit=False)
            for answer in answers:
                answer.question = question
                answer.save()
            messages.success(request, "Answers are added!!")
            return HttpResponseRedirect(question.get_absolute_url())

    return render(request, 'courses/answer_form.html', {'question': question,
                                                        # 'form': form
                                                        'formset': formset
                                                        })


# we are making the course list by teacher or say they have the user account in admin

def course_by_teacher(request, teacher_name):
    # here we are using the quesry to get the teacher then courses associated after that we take
    # it to get the courses  (this method much query time ) or other we can use filter
    # teacher = models.User.objects.get(username=teacher_name)
    # courses = teacher.course_set.all()
    courses = models.Course.objects.filter(teacher__username=teacher_name,
                                           published=True)
    # as course have teacher and teacher associated with username from the User model as teacher is the fk to
    # the User model __ helps to jump from one relation to another
    # and using this we didn't get 404 error
    return render(request, 'courses/course_list.html', {'courses': courses,
                                                        'email': email})


def search(request):
    # getting the search term
    term = request.GET.get('q')
    # here course model have title an actual thing and icontains get title which contains the term as i concern
    # as it is for the case sensitive eg: title = Apple q= apple still match
    courses = models.Course.objects.filter(Q(title__icontains=term) | Q(description__icontains=term),
                                           published=True)
    if courses:
        return render(request, 'courses/course_list.html', {'courses': courses,
                                                            'email': email})
    else:
        messages.error(request, "NO COURSES ARE THERE RELATED TO YOUR SEARCH QUERY!!")
        return render(request, 'courses/course_list.html', {'email': email})

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models


STATUS_CHOICES = (
    ('i','In Progress'),
    ('r', 'In Review'),
    ('p', 'Published'),
)

# Django contains a model as the user in django admin
# django has contrib directory contains useful section s like authentication 'auth'


# Create your models here.
class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(User)
    subject = models.CharField(default='', max_length=100)
    # updating the courses records as to mark them published =true
    # we make sure to not hit the  database bar bar as we use the for loop to update
    # so instead of that we use Courses.objects.update(published=true)
    # as same as Course.objects.all().update(published=True)
    # also we can't apply update on single it must be on the queryset
    published = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='i')

    # in order to delete the records we use the delete as
    # using the delete we can delete the single and the whole queryset
    #

    def __str__(self):
        return self.title

    def time_to_complete(self):
        from courses.templatetags.course_extras import time_estimate
        return '{} minutes.'.format(time_estimate(len(self.description.split())))


class Step(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course)

    # this defines us how our model view things or handle them
    class Meta:
        # making the Step model abstract
        abstract = True
        ordering = ['order', ]

    # here many steps belong to one course not a vice versa as one to many relation is there

    def __str__(self):
        return self.title


class Text(Step):
    content = models.TextField(blank=True, default='')

    def get_absolute_url(self):
        return reverse('courses:text',
                       kwargs={
                           'course_pk': self.course_id,
                           'step_pk': self.id
                       })


class Quiz(Step):
    total_questions = models.IntegerField(default=4)
    times_taken =  models.IntegerField(default=0, editable=False)

    class Meta:
        verbose_name_plural = "Quizzes"

    def get_absolute_url(self):
        return reverse('courses:quiz',
                       kwargs={
                           'course_pk': self.course_id,
                           'step_pk': self.id
                       })


class Question(models.Model):
    quiz = models.ForeignKey(Quiz)
    order = models.IntegerField(default=0)
    prompt = models.TextField()

    class Meta:
        ordering = ['order', ]

    def get_absolute_url(self):
        return self.quiz.get_absolute_url()

    def __str__(self):
        return self.prompt


class MultipleChoiceQuestion(Question):
    shuffle_answers = models.BooleanField(default=False)


class TrueFalseQuestion(Question):
    pass


class Answer(models.Model):
    question = models.ForeignKey(Question)
    order = models.IntegerField(default=0)
    text = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', ]

    def __str__(self):
        return self.text

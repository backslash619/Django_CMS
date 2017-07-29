from django import forms
from django.forms import inlineformset_factory

from . import models


class QuizForm(forms.ModelForm):
    class Meta:
        model = models.Quiz
        fields = [
            'title',
            'order',
            'description',
            'total_questions'
        ]


class TrueFalseQuestionForm(forms.ModelForm):
    class Meta:
        model = models.TrueFalseQuestion
        fields = [
            'order',
            'prompt',
        ]


class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = models.MultipleChoiceQuestion
        fields = [
            'order',
            'prompt',
            'shuffle_answers',
        ]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = [
            'order',
            'text',
            'correct'
        ]


AnswerFormSet = forms.modelformset_factory(
    models.Answer,
    form=AnswerForm,
    extra=2,
)

AnswerInlineFormSet = inlineformset_factory(
    models.Question,
    # models.Question is the one which we are saving with
    models.Answer,
    # models.Answer is the one we editing the forms
    extra=2,
    formset=AnswerFormSet,
    min_num=1,
    fields=['order',
            'text',
            'correct'
            ]
)

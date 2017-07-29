from datetime import date

from django.contrib import admin

from . import models


def make_published(modeladmin, request, queryset):
    queryset.update(status='p')


make_published.short_description = 'Mark selected courses as published.'


# custom filters
class TopicListFilter(admin.SimpleListFilter):
    title = 'By Topic'
    parameter_name = 'topic'

    def lookups(self, request, model_admin):
        return (
            ('python', 'Python'),
            ('ruby', 'Ruby'),
            ('java', 'Java')
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                title__contains=self.value()
            )


class YearListFilter(admin.SimpleListFilter):
    title = 'year created'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return (
            (2015, 2015),
            (2016, 2016),
            (2017, 2017)
        )

    def queryset(self, request, queryset):
        if self.value() == '2015':
            return queryset.filter(created_at__gte=date(2015, 1, 1),
                                   created_at__lte=date(2015, 12, 31))
        if self.value() == '2016':
            return queryset.filter(created_at__gte=date(2016, 1, 1),
                                   created_at__lte=date(2016, 12, 31))
        if self.value() == '2017':
            return queryset.filter(created_at__gte=date(2017, 1, 1),
                                   created_at__lte=date(2017, 12, 31))


# Register your models here.
class TextInline(admin.StackedInline):
    model = models.Text


class QuizInline(admin.StackedInline):
    model = models.Quiz


class AnswerInline(admin.TabularInline):
    model = models.Answer


class CourseAdmin(admin.ModelAdmin):
    inlines = [TextInline, QuizInline]
    search_fields = ['title',
                     'description']
    list_filter = ['created_at',
                   YearListFilter,
                   TopicListFilter]
    list_display = ['title',
                    'created_at',
                    'time_to_complete',
                    'status', ]
    list_editable = ['status']
    actions = [make_published]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline, ]
    search_fields = ['prompt']
    list_display = ['prompt',
                    'quiz',
                    'order']
    list_editable = ['quiz',
                     'order']
    radio_fields = {'quiz': admin.HORIZONTAL}


class QuizAdmin(admin.ModelAdmin):
    fields = ['course',
              'title',
              'description',
              'order',
              'total_questions']
    search_fields = ['title', 'description']

    list_filter = ['course']
    list_display = ['title',
                    'course',
                    'total_questions']
    list_editable = ['course', 'total_questions']


class TextAdmin(admin.ModelAdmin):
    # fields = ['course',
    #           'title',
    #           'order',
    #           'description',
    #           'content']
    fieldsets = (
        (None, {
            'fields': ('course',
                       'title',
                       'order',
                       'description',),
        }),
        ('Add Content', {
            'fields': ('content',),
            'classes': ('collapse',),
        }),
    )


# admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Text, TextAdmin)
admin.site.register(models.Quiz, QuizAdmin)
# admin.site.register(models.Question)
# not doing the Qestion and put the type into the question as to make admin con=mfortable to do things
admin.site.register(models.MultipleChoiceQuestion, QuestionAdmin)
admin.site.register(models.TrueFalseQuestion, QuestionAdmin)
# admin.site.register(models.Answer)

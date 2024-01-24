from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.db import models
from django.template.defaultfilters import slugify


class IsPublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=Survey.PublishedChoice.PUBLISHED)


class IsDraftManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=Survey.PublishedChoice.DRAFT)


class Survey(models.Model):
    class PublishedChoice(models.IntegerChoices):
        DRAFT = (0, 'Draft')
        PUBLISHED = (1, 'Published')
        __empty__ = 'Status'

    owner = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='surveys')
    title = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, editable=False, db_index=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    published = models.BooleanField(choices=PublishedChoice, default=PublishedChoice.DRAFT)
    users_pass = models.ManyToManyField(to=get_user_model(), related_name='passes_survey', blank=True)

    objects = models.Manager()
    is_published = IsPublishedManager()
    is_draft = IsDraftManager()

    def add_passed_user(self, user):
        self.users_pass.add(user)

    def passed_users(self):
        return self.users_pass.all()

    def how_many_user_passes(self):
        return self.users_pass.count()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('survey_statistic', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save()


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = ('MULTIPLE_CHOICE', 'Multiple choice')
        BINARY = ('BINARY', 'Binary (2 options)')
        DEFAULT = ('DEFAULT', 'One choice a couple answers')
        __empty__ = 'Question type'

    survey = models.ForeignKey('Survey', related_name='question', on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    question_type = models.CharField(choices=QuestionType, default=QuestionType.DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class Answer(models.Model):
    question = models.ForeignKey('Question', related_name='answers', on_delete=models.CASCADE)
    user = models.ManyToManyField(to=get_user_model(), related_name='answers', blank=True)
    answer = models.CharField(max_length=255)

    def add_user(self, user):
        self.user.add(user)

    def how_many_user_answered(self):
        return self.user.count()

    def __str__(self):
        return self.question.question + ' ' + self.answer[:50]

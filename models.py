from django.db import models
from django.conf import settings
from datetime import datetime
from django.apps import apps
from django.contrib.auth import get_user_model

class Author(models.Model):

    name = models.CharField(
        'name',
        max_length=50,
        blank=True,
        help_text='The name of the author'
    )

    def __str__(self):
        return f"{self.name}"


class Article(models.Model):

    title = models.CharField(
        'title',
        max_length=75,
        help_text='A short description of the article',
    )
    description = models.TextField(
        'description',
        blank=True,
        help_text='Details about the article'
    )
    publish_date = models.DateField(
        default=datetime.now,
        help_text='The date and time the article was published'
    )
    author = models.ForeignKey(
        Author,
        verbose_name='author',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='article_responsibility',
        help_text='The author primarily responsible for executing this article'
    )

    def __str__(self):
        return self.title


    class Meta:
        ordering=['-publish_date']


class DocumentAnchor(models.Model):
    article=models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        help_text='The article to which this note applies',
    )
    class Meta:
        ordering = ['id']

    @property
    def ordinal(self):
        return DocumentAnchor.objects.filter(article=self.article, id__lt=self.id).count()

    def __str__(self):
        return 'Anchor {} for {}'.format(self.ordinal, self.article)

class UploadedFile(models.Model):

    anchor=models.ForeignKey(
        DocumentAnchor,
        null=True,
        on_delete=models.SET_NULL,
        help_text='The anchor point of the article to which this file is attached',
    )
    title = models.CharField(
        'title',
        blank=True,
        max_length=255,
        help_text='The title of the document (may be the same or different from the article to which it is attached)'
    )
    upload_date = models.DateField(
        'Date Uploaded',
        auto_now=True,
    )
    file = models.FileField(
        'file',
        help_text='The uploaded file'
    )

    class Meta:
        ordering = ['upload_date',]

    def __str__(self):
        return self.title

class Link(models.Model):

    anchor=models.ForeignKey(
        DocumentAnchor,
        null=True,
        on_delete=models.SET_NULL,
        help_text='The anchor point of the article to which this file is attached',
    )
    title = models.CharField(
        'title',
        blank=True,
        max_length=255,
        help_text='The title of the link (may be the same or different from the article to which it is attached)'
    )
    href = models.URLField(
        'url',
        help_text = 'The url of the link'
    )

    def str(self):
        return self.href


class EnteredText(models.Model):

    anchor=models.ForeignKey(
        DocumentAnchor,
        null=True,
        on_delete=models.SET_NULL,
        help_text='The anchor point of the article to which this file is attached',
    )
    title = models.CharField(
        'title',
        blank=True,
        max_length=255,
        help_text='The title of the link (may be the same or different from the article to which it is attached)'
    )
    text = models.TextField(
        'text',
        help_text = 'The entered text'
    )

    def str(self):
        return self.title


class History(models.Model):

    when = models.DateTimeField(
        'when',
        auto_now_add=True,
        help_text='The date this change was made'
    )
    modelname = models.CharField(
        'model',
        max_length=50,
        help_text='The model to which this change applies'
    )
    objectid = models.BigIntegerField(
        'object id',
        null=True,
        blank=True,
        help_text='The id of the record that was changed'
    )
    fieldname = models.CharField(
        'field',
        max_length=50,
        help_text='The that was changed',
    )
    old_value = models.TextField(
        'old value',
        blank=True,
        null=True,
        help_text='The value of the field before the change'
    )
    new_value = models.TextField(
        'new value',
        blank=True,
        help_text='The value of the field after the change'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='flaxarticle_history',
        null=True,
        help_text='The user who made this change'
    )

    class Meta:
        ordering = ('-when', 'modelname', 'objectid')

    def __str__(self):

        new_value_trunc = self.new_value[:17:]+'...' if len(self.new_value) > 20 else self.new_value

        try:
            model = apps.get_model('flaxarticles', self.modelname)
            object = model.objects.get(pk=self.objectid)
            return f'{self.when.strftime("%Y-%m-%d")}: {self.modelname}: [{object}] [{self.fieldname}] changed to "{new_value_trunc}"'

        except Exception as e:
            print (e)

        return f'{"mdy".format(self.when.strftime("%Y-%m-%d"))}: {self.modelname}: {self.objectid} [{self.fieldname}] changed to "{new_value_trunc}"'



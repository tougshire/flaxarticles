from django import forms
from django.forms import inlineformset_factory
from .models import Author, Article, DocumentAnchor, Link, UploadedFile, EnteredText


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
          'name'
        ]

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title',
            'description',
            'publish_date',
            'author',
        ]

class DocumentAnchorForm(forms.ModelForm):
    class Meta:
        model = DocumentAnchor
        fields = [
            'article',
        ]

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile

        fields = [
            'anchor',
            'title',
            'file',
        ]

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = [
            'anchor',
            'title',
            'href',
        ]

class EnteredTextForm(forms.ModelForm):
    class Meta:
        model = EnteredText
        fields = [
            'anchor',
            'title',
            'text',
        ]

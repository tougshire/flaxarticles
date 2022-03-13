import sys
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import QueryDict
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from tougshire_vistas.models import Vista
from tougshire_vistas.views import (delete_vista, default_vista, get_global_vista,
                                    get_latest_vista, make_vista,
                                    retrieve_vista)

from .forms import (ArticleForm, AuthorForm, DocumentAnchorForm,EnteredTextForm, LinkForm, UploadedFileForm)
from .models import History, Article, Author


def update_history(form, modelname, object, user):
    for fieldname in form.changed_data:
        try:
            old_value = str(form.initial[fieldname]),
        except KeyError:
            old_value = None

        history = History.objects.create(
            user=user,
            modelname=modelname,
            objectid=object.pk,
            fieldname=fieldname,
            old_value=old_value,
            new_value=str(form.cleaned_data[fieldname])
        )

        history.save()



class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'flaxarticles.add_article'
    model = Article
    form_class = ArticleForm

    def get_success_url(self):
        return reverse_lazy('flaxarticles:article-detail', kwargs={'pk': self.object.pk})


class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'flaxarticles.change_article'

    model = Article
    form_class = ArticleForm

    def get_success_url(self):

        return reverse_lazy('flaxarticles:article-detail', kwargs={'pk': self.object.pk})

class ArticleDetail(DetailView):
    # permission_required = 'flaxarticles.view_article'
    model = Article

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['article_labels'] = {field.name: field.verbose_name.title(
        ) for field in Article._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        return context_data


class ArticleDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'flaxarticles.delete_article'
    model = Article
    success_url = reverse_lazy('flaxarticles:article-list')


class ArticleSoftDelete(PermissionRequiredMixin, UpdateView):
    permission_required = 'flaxarticles.delete_article'
    model = Article
    template_name = 'flaxarticles/item_confirm_delete.html'
    success_url = reverse_lazy('flaxarticles:article-list')
    fields = ['is_deleted']

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['article_labels'] = {field.name: field.verbose_name.title(
        ) for field in Article._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}
        context_data['articlenote_labels'] = {field.name: field.verbose_name.title(
        ) for field in ArticleNote._meta.get_fields() if type(field).__name__[-3:] != 'Rel'}

        return context_data

class ArticleList(ListView):
    # permission_required = 'flaxarticles.view_article'
    model = Article
    paginate_by = 30

    def setup(self, request, *args, **kwargs):

        self.vista_settings={
            'max_search_keys':5,
            'text_fields_available':[],
            'filter_fields_available':{},
            'order_by_fields_available':[],
            'columns_available':[]
        }

        self.vista_settings['text_fields_available']=[
            'title',
            'description',
            'completion_notes',
        ]

        self.vista_settings['filter_fields_available'] = [
            'title',
            'description',
            'publish_date',
            'author',
        ]

        for fieldname in [
            'title',
            'publish_date',
            'author',
        ]:
            self.vista_settings['order_by_fields_available'].append(fieldname)
            self.vista_settings['order_by_fields_available'].append('-' + fieldname)

        for fieldname in [
            'title',
            'description',
            'publish_date',
            'author',
        ]:
            self.vista_settings['columns_available'].append(fieldname)

        self.vista_settings['field_types'] = {
            'begin':'date',
        }

        self.vista_defaults = {
            'order_by': Article._meta.ordering,
            'filterop__status':'in',
            'filterfield__status': (1,2,3),
            'paginate_by':self.paginate_by
        }

        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset()

        self.vistaobj = {'querydict':QueryDict(), 'queryset':queryset}

        if 'delete_vista' in self.request.POST:
            delete_vista(self.request)

        if 'tag' in self.kwargs:
            print('tp m3df19', self.kwargs.get('tag'))
            tag = self.kwargs.get('tag')
            self.vistaobj['queryset'] = self.vistaobj['queryset'].filter(tags__id__in=[tag])
            print('tp m3df21', queryset
            )
        if 'vista_query_submitted' in self.request.POST:

            self.vistaobj = make_vista(
                self.request.user,
                queryset,
                self.request.POST,
                self.request.POST.get('vista_name') if 'vista_name' in self.request.POST else '',
                self.request.POST.get('make_default') if ('make_default') in self.request.POST else False,
                self.vista_settings
            )
        elif 'retrieve_vista' in self.request.POST:
            self.vistaobj = retrieve_vista(
                self.request.user,
                queryset,
                'flaxarticles.article',
                self.request.POST.get('vista_name'),
                self.vista_settings

            )
        elif 'default_vista' in self.request.POST:
            print('tp m38830', urllib.parse.urlencode(self.vista_defaults))
            self.vistaobj = default_vista(
                self.request.user,
                queryset,
                QueryDict(urllib.parse.urlencode(self.vista_defaults)),
                self.vista_settings
            )


        return self.vistaobj['queryset']

    def get_paginate_by(self, queryset):

        if 'paginate_by' in self.vistaobj['querydict'] and self.vistaobj['querydict']['paginate_by']:
            return self.vistaobj['querydict']['paginate_by']

        return super().get_paginate_by(self)

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)

        context_data['authors'] = Author.objects.all()

        context_data['order_by_fields_available'] = []
        for fieldname in self.vista_settings['order_by_fields_available']:
            if fieldname > '' and fieldname[0] == '-':
                context_data['order_by_fields_available'].append({ 'name':fieldname, 'label':Article._meta.get_field(fieldname[1:]).verbose_name.title() + ' [Reverse]'})
            else:
                context_data['order_by_fields_available'].append({ 'name':fieldname, 'label':Article._meta.get_field(fieldname).verbose_name.title()})

        context_data['columns_available'] = [{ 'name':fieldname, 'label':Article._meta.get_field(fieldname).verbose_name.title() } for fieldname in self.vista_settings['columns_available']]

        if self.request.user.is_authenticated:
            context_data['vistas'] = Vista.objects.filter(user=self.request.user, model_name='flaxarticles.article').all() # for choosing saved vistas

        if self.request.POST.get('vista_name'):
            context_data['vista_name'] = self.request.POST.get('vista_name')

        vista_querydict = self.vistaobj['querydict']

        #putting the index before item name to make it easier for the template to iterate
        context_data['filter'] = []
        for indx in range( self.vista_settings['max_search_keys']):
            cdfilter = {}
            cdfilter['fieldname'] = vista_querydict.get('filter__fieldname__' + str(indx)) if 'filter__fieldname__' + str(indx) in vista_querydict else ''
            cdfilter['op'] = vista_querydict.get('filter__op__' + str(indx) ) if 'filter__op__' + str(indx) in vista_querydict else ''
            cdfilter['value'] = vista_querydict.get('filter__value__' + str(indx)) if 'filter__value__' + str(indx) in vista_querydict else ''
            if cdfilter['op'] in ['in']:
                cdfilter['value'] = vista_querydict.getlist('filter__value__' + str(indx)) if 'filter__value__'  + str(indx) in vista_querydict else []
            context_data['filter'].append(cdfilter)

        context_data['order_by'] = vista_querydict.getlist('order_by') if 'order_by' in vista_querydict else Article._meta.ordering

        context_data['combined_text_search'] = vista_querydict.get('combined_text_search') if 'combined_text_search' in vista_querydict else ''

        context_data['article_labels'] = { field.name: field.verbose_name.title() for field in Article._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'flaxarticles.add_author'
    model = Author
    form_class = AuthorForm

    def get_success_url(self):
        if 'opener' in self.request.POST and self.request.POST['opener'] > '':
            return reverse_lazy('flaxarticles:author-close', kwargs={'pk': self.object.pk})
        else:
            return reverse_lazy('flaxarticles:author-detail', kwargs={'pk': self.object.pk})

        return response

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'flaxarticles.change_author'
    model = Author
    form_class = AuthorForm

    def get_success_url(self):
        return reverse_lazy('flaxarticles:author-detail', kwargs={'pk': self.object.pk})


class AuthorDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'flaxarticles.view_author'
    model = Author

    def get_context_data(self, **kwargs):

        context_data = super().get_context_data(**kwargs)
        context_data['author_labels'] = { field.name: field.verbose_name.title() for field in Author._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }

        return context_data

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'flaxarticles.delete_author'
    model = Author
    success_url = reverse_lazy('flaxarticles:author-list')

class AuthorList(PermissionRequiredMixin, ListView):
    permission_required = 'flaxarticles.view_author'
    model = Author

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['author_labels'] = { field.name: field.verbose_name.title() for field in Author._meta.get_fields() if type(field).__name__[-3:] != 'Rel' }
        return context_data

class AuthorClose(PermissionRequiredMixin, DetailView):
    permission_required = 'flaxarticles.view_author'
    model = Author
    template_name = 'flaxarticles/author_closer.html'


from django.views.generic.base import RedirectView
from django.urls import path, reverse_lazy
from . import views

app_name = 'flaxarticles'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('flaxarticles:article-list'))),
    path('article/', RedirectView.as_view(url=reverse_lazy('flaxarticles:article-list'))),
    path('article/create/', views.ArticleCreate.as_view(), name='article-create'),
    path('article/<int:pk>/update/', views.ArticleUpdate.as_view(), name='article-update'),
    path('article/<int:pk>/detail/', views.ArticleDetail.as_view(), name='article-detail'),
    path('article/<int:pk>/delete/', views.ArticleSoftDelete.as_view(), name='article-delete'),
    path('article/list/', views.ArticleList.as_view(), name='article-list'),
    path('author/', RedirectView.as_view(url=reverse_lazy('flaxarticles:author-list'))),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/detail/', views.AuthorDetail.as_view(), name='author-detail'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
    path('author/list/', views.AuthorList.as_view(), name='author-list'),
    path('author/<int:pk>/close/', views.AuthorClose.as_view(), name="author-close"),

]

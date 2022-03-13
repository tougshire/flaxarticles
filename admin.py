from django.contrib import admin
from .models import Article, Author, DocumentAnchor, Link, UploadedFile

class ArticleAdmin(admin.ModelAdmin):
    list_display=('title', 'author')
    fields=(
        'title',
        'description',
        'author',
        'publish_date',
    )

admin.site.register(Article, ArticleAdmin)

admin.site.register(Author)

class DocumentAnchorAdmin(admin.ModelAdmin):

    list_display=('article', 'ordinal')



admin.site.register(DocumentAnchor,DocumentAnchorAdmin)

admin.site.register(UploadedFile)

admin.site.register(Link)

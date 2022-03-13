from django.contrib import admin
from .models import Article, Author, DocumentAnchor, Link, Tag, UploadedFile

class ArticleAdmin(admin.ModelAdmin):

    fields=(
        'title',
        'description',
        'author',
        'publish_date',
        'tags'
    )

admin.site.register(Article, ArticleAdmin)

admin.site.register(Author)

class DocumentAnchorAdmin(admin.ModelAdmin):

    list_display=('article', 'ordinal')


admin.site.register(DocumentAnchor,DocumentAnchorAdmin)

admin.site.register(UploadedFile)

admin.site.register(Link)

admin.site.register(Tag)

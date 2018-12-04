from django.contrib import admin

from .models import *

class PostAdmin(admin.ModelAdmin):
    list_display = ('short_url', 'warc_size_kb', 'retry_count', 'state')
    list_filter = ('retry_count', 'state',)

class PostInline(admin.TabularInline):
    model = Post

class SeedAdmin(admin.ModelAdmin):
    list_display = ('seed', 'created_at', 'collection', 'last_check', 'state')
    list_filter = ('state', )
    inlines = [PostInline,]

class SeedInline(admin.TabularInline):
    model = Seed


class CollectionAdmin(admin.ModelAdmin):
   inlines = [
        SeedInline,
    ]

        

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Seed, SeedAdmin)
admin.site.register(Post, PostAdmin)

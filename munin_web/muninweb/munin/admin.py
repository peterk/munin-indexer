from django.contrib import admin

from .models import *

class PostAdmin(admin.ModelAdmin):
    list_display = ('short_url', 'uid', 'warc_size_kb', 'created_at', 'retry_count', 'state')
    list_filter = ('retry_count', 'state', 'created_at')
    search_fields = ('jobid', 'uid', 'url')

class PostInline(admin.TabularInline):
    model = Post

class SeedAdmin(admin.ModelAdmin):
    list_display = ('seed', 'created_at', 'collection', 'last_check', 'state')
    list_filter = ('state', )
    #inlines = [PostInline,]

class SeedInline(admin.TabularInline):
    model = Seed

class CollectionAdmin(admin.ModelAdmin):
    pass

        
class StatAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'warc_count', 'warcs_created', 'post_crawl_queue', 'post_count', 'seed_count', 'warc_size_total', 'retry_count')



admin.site.site_header = 'Munin'

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Seed, SeedAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Stats, StatAdmin)

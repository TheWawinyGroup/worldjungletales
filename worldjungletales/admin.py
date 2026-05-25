from django.contrib import admin

from worldjungletales.models import Article, Comment, Subscriber, Topic


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "topic",
        "article_type",
        "featured",
        "editor_pick",
        "status",
        "published_on",
    )
    list_filter = ("status", "topic", "article_type", "featured", "editor_pick")
    search_fields = ["title", "subtitle", "excerpt", "content"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views_count",)


class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "status", "created_on")
    list_filter = ("status",)
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Article, ArticleAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Comment)
admin.site.register(Subscriber)

from django.urls import path
from django.views.generic import TemplateView

from worldjungletales import backoffice_views, views
from worldjungletales.feeds import LatestArticlesFeed

urlpatterns = [
    path("", views.home, name="home"),
    path("topics/<slug:slug>/", views.topics, name="topics"),
    path("articles/<slug:slug>/", views.article, name="article"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("comment/<int:article_pk>/", views.comment, name="comment"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about/", views.about, name="about"),
    path("archive/", views.archive, name="archive"),
    path("authors/<str:username>/", views.author_profile, name="author_profile"),
    path("newsletter/", views.newsletter, name="newsletter"),
    path("rss/", LatestArticlesFeed(), name="rss"),
    path("write-for-us/", views.write_for_us, name="write_for_us"),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="worldjungletales/robots.txt", content_type="text/plain"
        ),
    ),
    # backoffice
    path("backoffice/", backoffice_views.backoffice, name="backoffice"),
    path("backoffice/topics/", backoffice_views.all_topics, name="all_topics"),
    path("backoffice/topics/new/", backoffice_views.topic_new, name="topic_new"),
    path("backoffice/articles/", backoffice_views.articles, name="articles"),
    path("backoffice/articles/new/", backoffice_views.article_new, name="article_new"),
    path(
        "backoffice/articles/<int:pk>/edit/",
        backoffice_views.article_edit,
        name="article_edit",
    ),
    path("backoffice/drafts/", backoffice_views.drafts, name="drafts"),
    path(
        "backoffice/drafts/<int:article_pk>/",
        backoffice_views.draft_publish,
        name="draft_publish",
    ),
    path(
        "backoffice/articles/<int:article_pk>/",
        backoffice_views.unpublish,
        name="unpublish",
    ),
]

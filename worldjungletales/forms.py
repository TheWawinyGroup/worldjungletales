from django import forms

from worldjungletales.models import Article, Comment, Subscriber, Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = "__all__"


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "subtitle",
            "excerpt",
            "topic",
            "article_type",
            "content",
            "image_caption",
            "image_credit",
            "author_bio",
            "featured",
            "editor_pick",
            "hero_priority",
            "series",
            "seo_title",
            "seo_description",
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["email", "comment"]


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = "__all__"

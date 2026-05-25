from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from common.supabase import StorageClient
from worldjungletales.models import Article, ArticleView, Comment, Topic

from .forms import ArticleForm, TopicForm

UserModel = get_user_model()


@user_passes_test(lambda u: u.is_superuser)
def backoffice(request):
    context = {}
    qs = Article.objects.all()
    published_count = qs.filter(status=1).count()
    topics_count = Topic.objects.count()

    comments_qs = Comment.objects.all()
    comments_count = comments_qs.count()

    today_start = timezone.now().date()
    today_comment_count = comments_qs.filter(created_on__date=today_start).count()

    views_qs = ArticleView.objects.all()
    article_views_count = views_qs.count()
    today = timezone.now().date()

    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - timedelta(days=7)
    end_of_last_week = start_of_this_week - timedelta(seconds=1)

    this_week_views_qs = ArticleView.objects.filter(
        created_on__date__gte=start_of_this_week
    )
    last_week_views_qs = ArticleView.objects.filter(
        created_on__date__range=(start_of_last_week, end_of_last_week)
    )

    this_week_count = this_week_views_qs.count()
    last_week_count = last_week_views_qs.count()

    if last_week_count == 0:
        percentage_change = 100  # 100% growth if last week had 0 views
    else:
        percentage_change = (
            (this_week_count - last_week_count) / last_week_count
        ) * 100

    # Views by date (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    views_by_date = (
        views_qs.filter(article__in=qs, created_on__gte=thirty_days_ago)
        .extra({"date": "date(created_on)"})
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # Views by region  # Top 10 countries
    views_by_region = (
        views_qs.filter(article__in=qs)
        .exclude(country__isnull=True)
        .values("country")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    context["articles"] = qs[:5]
    context["published_count"] = published_count
    context["comments_count"] = comments_count
    context["today_comment_count"] = today_comment_count
    context["topics_count"] = topics_count
    context["article_views_count"] = article_views_count
    context["article_view_pc_change"] = percentage_change
    context["views_by_region"] = views_by_region
    context["views_by_date"] = views_by_date
    return render(request, "worldjungletales/backoffice/dashboard.html", context)


@user_passes_test(lambda u: u.is_superuser)
def all_topics(request):
    context = {}
    topics = Topic.objects.all()
    context["topics"] = topics
    return render(request, "worldjungletales/backoffice/topics.html", context)


@user_passes_test(lambda u: u.is_superuser)
def topic_new(request):
    context = {}
    if request.method == "POST":
        form = TopicForm(request.data)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.slug = topic.title.replace(" ", "-")
            topic.save()
            messages.success(request, "Successfully created a topic")
            return render(
                request, "worldjungletales/backoffice/create_topic.html", context
            )

    else:
        form = TopicForm()
    return render(
        request, "worldjungletales/backoffice/create_topic.html", {"form": form}
    )


@user_passes_test(lambda u: u.is_superuser)
def articles(request):
    topics = Topic.objects.filter(status=1)
    articles = Article.objects.filter(author=request.user, status=1)
    context = {}
    context["articles"] = articles
    context["topics"] = topics

    return render(request, "worldjungletales/backoffice/articles.html", context)


@user_passes_test(lambda u: u.is_superuser)
def article_new(request):
    context = {}
    context["form"] = ArticleForm()

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            s = StorageClient()
            article.image_url = s.upload_article_cover(request)
            article.save()
            messages.success(request, "Succcessfuly Posted an article.")
            return redirect("drafts")
        else:
            context["form"] = form
            messages.error(request, "An error occurred! Please fix the errors below!")

    topics = Topic.objects.filter(status=1)
    context["topics"] = topics
    return render(request, "worldjungletales/backoffice/new_article.html", context)


@user_passes_test(lambda u: u.is_superuser)
def article_edit(request, pk):
    old_article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=old_article)
        if form.is_valid():
            article = form.save(commit=False)
            s = StorageClient()
            article.image_url = s.upload_article_cover(request, old_article.image_url)
            article.save()
            messages.success(request, "Successfully edited the article!")
            return redirect("drafts")
    else:
        form = ArticleForm(instance=old_article)

    topics = Topic.objects.filter(status=1)
    context = {
        "form": form,
        "article": old_article,
        "topics": topics,
    }
    return render(request, "worldjungletales/backoffice/edit_article.html", context)


@user_passes_test(lambda u: u.is_superuser)
def drafts(request):
    articles = Article.objects.filter(status=0)
    topics = Topic.objects.filter(status=1)
    context = {}
    context["articles"] = articles
    context["topics"] = topics

    return render(request, "worldjungletales/backoffice/draft_articles.html", context)


@user_passes_test(lambda u: u.is_superuser)
def draft_publish(request, article_pk):
    articles = Article.objects.filter(status=0)
    Article.objects.filter(pk=article_pk).update(status=1, published_on=timezone.now())
    topics = Topic.objects.filter(status=1)
    context = {}
    context["articles"] = articles
    context["topics"] = topics

    return redirect("drafts")


@user_passes_test(lambda u: u.is_superuser)
def unpublish(request, article_pk):
    author = request.user
    articles = Article.objects.filter(author=author, status=1)
    Article.objects.filter(author=author, pk=article_pk).update(status=0)
    topics = Topic.objects.filter(status=1)
    context = {}
    context["articles"] = articles
    context["topics"] = topics

    return redirect("articles")

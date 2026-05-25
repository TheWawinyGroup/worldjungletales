from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

import requests

from common.recaptcha import Recaptcha
from worldjungletales.forms import CommentForm, SubscribeForm
from worldjungletales.models import Article, ArticleView, Comment, Topic

UserModel = get_user_model()


def about(request):
    ctx = {}
    topics = Topic.objects.filter(status=1)
    ctx["topics"] = topics
    return render(request, "worldjungletales/blog/about.html", ctx)


def write_for_us(request):
    ctx = {}
    topics = Topic.objects.filter(status=1)
    ctx["topics"] = topics
    return render(request, "worldjungletales/blog/write_for_us.html", ctx)


def comment(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    topics = Topic.objects.filter(status=1)

    if request.method == "POST":
        recaptcha_response = request.POST.get("g-recaptcha-response")
        r = Recaptcha()
        result = r.verify(recaptcha_response)

        if not result:
            return redirect("article", slug=article.slug)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect("article", slug=article.slug)
    else:
        form = CommentForm()

    context = {
        "article": article,
        "topics": topics,
        "form": form,
        "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
    }

    return render(request, "worldjungletales/blog/article.html", context)


def subscribe(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("home")

    else:
        form = SubscribeForm()

    return redirect("home")


def privacy_policy(request):
    topics = Topic.objects.filter(status=1)
    return render(
        request, "worldjungletales/blog/privacy_policy.html", {"topics": topics}
    )


def error_404(request, exception):
    topics = Topic.objects.filter(status=1)
    return render(request, "worldjungletales/blog/404.html", {"topics": topics})


def error_500(request):
    topics = Topic.objects.filter(status=1)
    return render(request, "worldjungletales/blog/500.html", {"topics": topics})


def home(request):
    topics = Topic.objects.filter(status=1)
    qs = Article.objects.filter(status=1).order_by("-published_on", "-created_on")
    if q := request.GET.get("q"):
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(subtitle__icontains=q)
            | Q(excerpt__icontains=q)
            | Q(content__icontains=q)
            | Q(topic__title__icontains=q)
        ).distinct()

    featured = list(
        qs.filter(featured=True).order_by("hero_priority", "-published_on")[:5]
    )
    lead_story = featured[0] if featured else qs.first()
    lead_id = lead_story.id if lead_story else None
    secondary_stories = [
        article for article in featured[1:5] if article.id != lead_id
    ] or list(qs.exclude(id=lead_id)[:4])
    latest = qs.exclude(id__in=[article.id for article in [lead_story] if article])[:8]
    editor_picks = qs.filter(editor_pick=True).exclude(id=lead_id)[:4]
    photo_essays = qs.filter(article_type="photo_essay")[:4]
    most_read = (
        qs.annotate(view_total=Count("views_data"))
        .filter(view_total__gt=0)
        .order_by("-view_total", "-published_on")[:5]
    )

    section_groups = []
    for topic in topics[:4]:
        section_articles = qs.filter(topic=topic)[:3]
        if section_articles:
            section_groups.append({"topic": topic, "articles": section_articles})

    context = {
        "topics": topics,
        "articles": qs[:12],
        "lead_story": lead_story,
        "secondary_stories": secondary_stories,
        "latest": latest,
        "editor_picks": editor_picks,
        "photo_essays": photo_essays,
        "most_read": most_read,
        "section_groups": section_groups,
        "query": q,
    }

    return render(request, "worldjungletales/blog/home.html", context)


def topics(request, slug):
    topics = Topic.objects.filter(status=1)
    topic = get_object_or_404(Topic, slug=slug)
    articles = Article.objects.filter(topic=topic, status=1).order_by(
        "-published_on", "-updated_on"
    )
    lead_story = articles.filter(featured=True).first() or articles.first()
    article_list = articles.exclude(id=lead_story.id) if lead_story else articles

    return render(
        request,
        "worldjungletales/blog/articles.html",
        {
            "articles": article_list,
            "topics": topics,
            "topic": topic,
            "lead_story": lead_story,
        },
    )


def track_article_view(request, article):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key

    geo_data = {}
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
        if response.status_code == 200:
            geo_data = response.json()
    except requests.RequestException:
        pass

    ArticleView.objects.create(
        article=article,
        ip_address=ip,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        referrer=request.META.get("HTTP_REFERER", ""),
        session_id=session_id,
        region=geo_data.get("region"),
        country=geo_data.get("country"),
        city=geo_data.get("city"),
    )


def article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    # Track views only if the visitor is NOT the article author (admin)
    if not request.user.is_authenticated or request.user != article.author:
        track_article_view(request, article)

    topics = Topic.objects.filter(status=1)
    comments = Comment.objects.filter(article=article)
    published = Article.objects.filter(status=1).exclude(id=article.id)
    recent = published.order_by("-published_on", "-created_on")[:4]
    related = published.filter(topic=article.topic)[:3]
    editor_picks = published.filter(editor_pick=True)[:4]
    most_read = (
        published.annotate(view_total=Count("views_data"))
        .filter(view_total__gt=0)
        .order_by("-view_total", "-published_on")[:4]
    )

    context = {
        "article": article,
        "topics": topics,
        "comments": comments,
        "recents": recent,
        "related": related,
        "editor_picks": editor_picks,
        "most_read": most_read,
        "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
    }

    return render(
        request,
        "worldjungletales/blog/article.html",
        context,
    )


def archive(request):
    topics = Topic.objects.filter(status=1)
    articles = Article.objects.filter(status=1).order_by("-published_on", "-created_on")
    return render(
        request,
        "worldjungletales/blog/archive.html",
        {"articles": articles, "topics": topics},
    )


def author_profile(request, username):
    topics = Topic.objects.filter(status=1)
    author = get_object_or_404(UserModel, username=username)
    articles = Article.objects.filter(author=author, status=1).order_by(
        "-published_on", "-created_on"
    )
    return render(
        request,
        "worldjungletales/blog/author.html",
        {"profile_author": author, "articles": articles, "topics": topics},
    )


def newsletter(request):
    topics = Topic.objects.filter(status=1)
    return render(request, "worldjungletales/blog/newsletter.html", {"topics": topics})

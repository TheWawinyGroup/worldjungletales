from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

STATUS = ((0, "Draft"), (1, "Publish"))
ARTICLE_TYPES = (
    ("feature", "Feature"),
    ("dispatch", "Field Dispatch"),
    ("guide", "Guide"),
    ("interview", "Interview"),
    ("photo_essay", "Photo Essay"),
    ("news", "News"),
    ("profile", "Species Profile"),
)


class AbstractBaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_on"]
        abstract = True


class Topic(AbstractBaseModel):
    title = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)
    status = models.IntegerField(choices=STATUS, default=0)

    @property
    def article_count(self):
        return Article.objects.filter(topic=self).count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("topics", args=[str(self.slug)])


class Article(AbstractBaseModel):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    image_url = models.URLField()
    subtitle = models.CharField(max_length=255, blank=True)
    excerpt = models.TextField(blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    article_type = models.CharField(
        max_length=20, choices=ARTICLE_TYPES, default="feature"
    )
    content = models.TextField()
    image_caption = models.CharField(max_length=255, blank=True)
    image_credit = models.CharField(max_length=120, blank=True)
    author_bio = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    editor_pick = models.BooleanField(default=False)
    hero_priority = models.PositiveSmallIntegerField(default=0)
    series = models.CharField(max_length=120, blank=True)
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.CharField(max_length=255, blank=True)
    published_on = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=0)

    @property
    def views_count(self):
        return self.views_data.count()

    @property
    def display_excerpt(self):
        if self.excerpt:
            return self.excerpt
        return strip_tags(self.content)[:180]

    @property
    def read_time(self):
        word_count = len(strip_tags(self.content).split())
        return max(1, round(word_count / 220))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.status == 1 and not self.published_on:
            self.published_on = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article", args=[str(self.slug)])


class ArticleView(AbstractBaseModel):
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, related_name="views_data"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Comment(AbstractBaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return self.comment


class Subscriber(AbstractBaseModel):
    email = models.EmailField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.email

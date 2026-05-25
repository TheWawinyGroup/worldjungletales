from django.contrib.syndication.views import Feed

from worldjungletales.models import Article


class LatestArticlesFeed(Feed):
    title = "World Jungle Tales"
    link = "/"
    description = "Wildlife, jungle ecosystems, conservation, safari culture, and nature travel."

    def items(self):
        return Article.objects.filter(status=1).order_by("-published_on", "-created_on")[
            :20
        ]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.display_excerpt

    def item_pubdate(self, item):
        return item.published_on or item.created_on

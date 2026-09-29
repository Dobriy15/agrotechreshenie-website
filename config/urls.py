from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, reverse
from django.views.generic import TemplateView

from core import views
from core.models import Category, Service


class StaticSitemap(Sitemap):
    priority = 1.0

    def items(self):
        return ["home"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.filter(status=Category.ACTIVE)


class ServiceSitemap(Sitemap):
    def items(self):
        return Service.objects.select_related("category").filter(category__status=Category.ACTIVE)


urlpatterns = [
    path("", views.home, name="home"),
    path("uslugi/<slug:slug>/", views.category, name="category"),
    path("uslugi/<slug:category_slug>/<slug:slug>/", views.service, name="service"),
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"static": StaticSitemap, "categories": CategorySitemap, "services": ServiceSitemap}},
    ),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

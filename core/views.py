from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Category, Review, Service, Stat


def home(request):
    return render(
        request,
        "core/home.html",
        {
            "stats": Stat.objects.all(),
            "categories": Category.objects.all(),
            "reviews": Review.objects.filter(is_published=True),
        },
    )


def category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    if not cat.is_active:
        raise Http404
    return render(
        request,
        "core/category.html",
        {"category": cat, "services": cat.services.prefetch_related("media")},
    )


def service(request, category_slug, slug):
    obj = get_object_or_404(
        Service.objects.select_related("category"), category__slug=category_slug, slug=slug
    )
    return render(request, "core/service.html", {"service": obj, "media": obj.media.all()})

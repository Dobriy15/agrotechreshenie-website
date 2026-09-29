from .models import Category, SiteSettings


def site(request):
    return {
        "site": SiteSettings.load(),
        "nav_categories": Category.objects.all(),
    }

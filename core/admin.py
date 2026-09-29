from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Review, Service, ServiceMedia, SiteSettings, Stat

admin.site.site_header = "АгроТехРешение — управление сайтом"
admin.site.site_title = "АТР админка"
admin.site.index_title = "Содержимое сайта"


def preview(url, h=60):
    return format_html('<img src="{}" style="height:{}px;border-radius:6px">', url, h) if url else "—"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Главный экран", {"fields": ["hero_title", "hero_subtitle", "hero_image"]}),
        ("Блоки главной", {"fields": ["services_title", "about_title", "about_html"]}),
        (
            "Контакты",
            {
                "fields": [
                    "phone_1",
                    "phone_2",
                    "production_address",
                    "office_address",
                    ("map_lat", "map_lon"),
                    "instagram_url",
                    "telegram_url",
                ]
            },
        ),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Stat)
class StatAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["value", "label"]


class ServiceInline(SortableTabularInline):
    model = Service
    fields = ["title", "slug"]
    extra = 0
    show_change_link = True
    prepopulated_fields = {}


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["title", "status", "thumb"]
    prepopulated_fields = {"slug": ["title"]}
    inlines = [ServiceInline]

    @admin.display(description="Фото")
    def thumb(self, obj):
        return preview(obj.image.url if obj.image else "")


class MediaInline(SortableTabularInline):
    model = ServiceMedia
    fields = ["thumb_preview", "image", "video"]
    readonly_fields = ["thumb_preview"]
    extra = 0

    @admin.display(description="Превью")
    def thumb_preview(self, obj):
        if obj.thumb:
            return preview(obj.thumb.url, 80)
        return "видео" if obj.video else "—"


@admin.register(Service)
class ServiceAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["title", "category", "photos_count"]
    list_filter = ["category"]
    prepopulated_fields = {"slug": ["title"]}
    fields = ["category", "title", "card_title", "slug", "text_html", "card_image", "autoplay_seconds"]
    inlines = [MediaInline]

    @admin.display(description="Фото")
    def photos_count(self, obj):
        return obj.media.count()


@admin.register(Review)
class ReviewAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["name", "role", "is_published"]
    list_editable = ["is_published"]

from django.db import models
from django.urls import reverse

from .images import process_image


class SiteSettings(models.Model):
    """Одна запись с общими данными сайта (контакты, hero, тексты главной)."""

    hero_title = models.CharField("Заголовок главного экрана", max_length=200)
    hero_subtitle = models.TextField("Подзаголовок главного экрана")
    hero_image = models.ImageField("Фон главного экрана", upload_to="site/")
    about_title = models.CharField("Заголовок «О компании»", max_length=100, default="О компании")
    about_html = models.TextField(
        "Текст «О компании» (HTML)",
        help_text="Можно использовать <p>, <strong>, <br>. Абзацы — в <p>.",
    )
    services_title = models.CharField(
        "Заголовок блока услуг", max_length=200, default="Какие виды услуг предлагает компания"
    )
    phone_1 = models.CharField("Телефон 1", max_length=30, blank=True)
    phone_2 = models.CharField("Телефон 2", max_length=30, blank=True)
    production_address = models.CharField("Адрес производства", max_length=200, blank=True)
    office_address = models.CharField("Адрес офиса", max_length=200, blank=True)
    map_lat = models.FloatField("Широта производства", default=53.87009)
    map_lon = models.FloatField("Долгота производства", default=27.51353)
    instagram_url = models.URLField("Instagram", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1  # всегда одна запись
        process_image(self.hero_image)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.filter(pk=1).first()


class Stat(models.Model):
    value = models.CharField("Число", max_length=20, help_text="Например: 500+")
    label = models.CharField("Подпись", max_length=60)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Счётчик"
        verbose_name_plural = "Счётчики (под главным экраном)"

    def __str__(self):
        return f"{self.value} {self.label}"


class Category(models.Model):
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    STATUS_CHOICES = [(ACTIVE, "Работает"), (IN_PROGRESS, "В процессе реализации")]

    title = models.CharField("Название", max_length=100)
    slug = models.SlugField("Адрес (латиницей)", unique=True)
    image = models.ImageField("Фото карточки", upload_to="categories/")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Направление"
        verbose_name_plural = "Направления (карточки на главной)"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        process_image(self.image, max_side=1200)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == self.ACTIVE

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class Service(models.Model):
    category = models.ForeignKey(
        Category, verbose_name="Направление", on_delete=models.CASCADE, related_name="services"
    )
    title = models.CharField("Название", max_length=150)
    card_title = models.CharField(
        "Название на карточке", max_length=150, blank=True, help_text="Если пусто — как название"
    )
    slug = models.SlugField("Адрес (латиницей)")
    text_html = models.TextField("Описание (HTML)", help_text="Абзацы — в <p>, переносы — <br>.")
    card_image = models.ImageField(
        "Фото карточки",
        upload_to="services/cards/",
        blank=True,
        help_text="Если пусто — берётся первое фото из галереи",
    )
    autoplay_seconds = models.PositiveSmallIntegerField("Смена фото, сек", default=2)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        unique_together = [("category", "slug")]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        process_image(self.card_image, max_side=1200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("service", args=[self.category.slug, self.slug])

    @property
    def card_label(self):
        return self.card_title or self.title

    @property
    def card_image_url(self):
        if self.card_image:
            return self.card_image.url
        first = self.media.exclude(image="").first()
        return first.thumb.url if first and first.thumb else ""


class ServiceMedia(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="media")
    image = models.ImageField("Фото", upload_to="services/photos/", blank=True)
    thumb = models.ImageField(upload_to="services/thumbs/", blank=True, editable=False)
    video = models.FileField(
        "Видео (mp4)", upload_to="services/video/", blank=True, help_text="Вместо фото, если нужно"
    )
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Фото/видео"
        verbose_name_plural = "Фото и видео для слайдера"

    def __str__(self):
        return (self.image or self.video).name.rsplit("/", 1)[-1]

    def save(self, *args, **kwargs):
        process_image(self.image, thumb_field=self.thumb)
        super().save(*args, **kwargs)


class Review(models.Model):
    name = models.CharField("Имя", max_length=100)
    role = models.CharField("Должность / кто", max_length=150, blank=True)
    text = models.TextField("Текст отзыва")
    is_published = models.BooleanField("Показывать", default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.name

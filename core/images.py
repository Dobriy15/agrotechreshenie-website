"""Приведение загруженных фото к вебу: поворот по EXIF, ресайз, WebP."""
from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

FULL_SIZE = 1920
THUMB_SIZE = 900
QUALITY = 80


def _to_webp(img: Image.Image, max_side: int) -> ContentFile:
    img = img.copy()
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, "WEBP", quality=QUALITY, method=6)
    return ContentFile(buf.getvalue())


def process_image(field_file, thumb_field=None, max_side=FULL_SIZE):
    """Перезаписывает field_file оптимизированным WebP и (опционально) заполняет превью.

    Вызывается из save() моделей только когда файл новый (не .webp от нас).
    """
    if not field_file or field_file.name.endswith(".webp"):
        return False
    # если исходник уже лежит в хранилище (сохранён через .save()), удалим его после конвертации
    old_name = field_file.name if field_file._committed else None
    storage = field_file.storage
    field_file.open("rb")
    img = Image.open(field_file)
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
    stem = Path(field_file.name).stem
    field_file.save(f"{stem}.webp", _to_webp(img, max_side), save=False)
    if thumb_field is not None:
        thumb_field.save(f"{stem}_thumb.webp", _to_webp(img, THUMB_SIZE), save=False)
    img.close()
    if old_name and old_name != field_file.name:
        storage.delete(old_name)
    return True

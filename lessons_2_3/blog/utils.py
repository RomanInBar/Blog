import io
from pathlib import Path

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from PIL import Image


def pagination(request, obj_list, count_obj):
    """Функция-пагинатор."""
    paginator = Paginator(obj_list, count_obj)
    page = request.GET.get('page')
    try:
        objs = paginator.page(page)
    except PageNotAnInteger:
        objs = paginator.page(1)
    except EmptyPage:
        objs = paginator.page(paginator.num_pages)
    return (objs, page)


def converter(obj):
    """Функция конвертации формата изображений в webp."""
    new_file_name = str(Path(obj.name).with_suffix('.webp'))
    image = Image.open(obj.file)
    thumb_io = io.BytesIO()
    image.save(thumb_io, 'webp', optimize=True, quality=95)
    new_obj = InMemoryUploadedFile(
        thumb_io,
        obj.name,
        new_file_name,
        size=obj.size,
        charset='utf-8',
        content_type='image/jpeg',
    )
    return new_obj

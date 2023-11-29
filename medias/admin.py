from django.contrib import admin
from medias.models import Photo, Video


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "description")
    list_display_links = ("id", "room")


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass

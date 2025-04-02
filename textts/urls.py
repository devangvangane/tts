from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from ttspeech.views import text_to_speech, delete_audio, home, file_to_speech

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("text-to-speech/", text_to_speech, name="text_to_speech"),
    path("file-to-speech/", file_to_speech, name="file_to_speech"),
    path("delete-audio/", delete_audio, name="delete_audio"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

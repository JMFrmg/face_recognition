from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('face_detection.urls')),
    path('admin/', admin.site.urls),
]

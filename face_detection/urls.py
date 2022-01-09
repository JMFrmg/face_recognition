from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("predict/", views.identify_faces, name="predict"),
    path("update_face_data/", views.update_face_data, name="update_face"),
    path("model_accuracy_test/", views.model_accuracy_test),
]
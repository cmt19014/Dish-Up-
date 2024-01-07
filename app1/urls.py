from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cooking_data/', views.cooking_data_list, name='cooking_data_list'),
    path('upload/', views.upload_and_process_image, name='upload_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

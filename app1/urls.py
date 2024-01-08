from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('cooking_data/', views.cooking_data_list, name='cooking_data_list'),
    path('upload/', views.upload_and_process_image, name='upload_image'),
    path('update-dish-color/<int:dish_id>/', views.update_dish_color, name='update_dish_color'),
    path('reset-database/', views.reset_database, name='reset_database'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

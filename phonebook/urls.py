from django.urls import path
from .views import *


urlpatterns = [
    path('', phones_list, name='phone_list_url'),
    path('upload/', phones_upload)
]

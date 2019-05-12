from django.urls import path
from .views import *


urlpatterns = [
    path('', phones_list)
]

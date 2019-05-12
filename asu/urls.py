from django.urls import path
from .views import *


urlpatterns = [
    path('detail/', call_detail_list),
    path('upload/', detail_upload)
]

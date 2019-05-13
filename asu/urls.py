from django.urls import path
from .views import *


urlpatterns = [
    path('detail/', call_detail_list, name='detail_list_url'),
    path('upload/', detail_upload),
    path('sum/', get_sum),
    path('chsum/', get_sum_otd)
]

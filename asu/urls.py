from django.urls import path
from .views import *


urlpatterns = [
    path('detail/', call_detail_list, name='detail_list_url'),
    path('upload/', detail_upload),
    path('sum/', get_sum),
    path('chsum/', get_sum_otd),
    path('download/', download_sum_all_otd, name='get_data'),
    path('download_otd/', download_sum_otd, name='get_data_for_org'),
    path('download_intr/', give_intruders, name='get_ch_intruders'),
    path('visualizator/', visualize_sum_month, name='visualize')
]

from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginFormView.as_view()),
    path('logout/', LogoutView.as_view()),
]

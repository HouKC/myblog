from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index),
    re_path(r'^profile/$', views.profile, name='profile'),
    re_path(r'^profile/update/$', views.profile_update, name='profile_update'),
]

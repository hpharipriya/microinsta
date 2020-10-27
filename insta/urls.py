from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
   path('add/', views.add, name='add'),
   path('follow/', views.follow, name='follow'),
    #url(r'add/', views.PostImage.as_view(), name='add'),
]

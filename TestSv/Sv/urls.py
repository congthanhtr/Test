from django.urls import path

from . import views


urlpatterns = [
    path('v1/weather_forecast', views.weather_forecast, name='weather_forecast'),
    path('v1/recommend', views.recommend, name='recommend'),
    path('v2/recommend', views.recommend_v2, name='recommend_v2')
]

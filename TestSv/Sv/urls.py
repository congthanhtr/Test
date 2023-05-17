from django.urls import path

from . import views


urlpatterns = [
    path('v1/weather_forecast', views.weather_forecast, name='weather_forecast'),
    path('v1/recommend', views.recommend, name='recommend'),
    path('v2/recommend', views.recommend_v2, name='recommend_v2'),
    path('v2/poi/recommend', views.poi_recommend, name='poi_recommend'),
    path('v2/poi/find', views.poi_find, name='poi_find'), # find info about a place by its address
    path('v2/poi/find/<str:xid>', views.poi_find_by_xid, name='poi_find_by_xid'),
    path('v2/poi', views.poi_add_and_update, name='poi_add_and_update'), # add and update api
    path('v2/poi/delete/<str:xid>', views.poi_delete_by_xid, name='poi_delete_by_xid')
]

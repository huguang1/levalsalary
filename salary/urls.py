
from django.contrib import admin
from django.urls import path
import xadmin
from django.conf.urls import url
from salary.views import IndexView, SearchView
urlpatterns = [
    url(r'index$', IndexView.as_view(), name='index'),
    url(r'^$', SearchView.as_view(), name='search'),
]






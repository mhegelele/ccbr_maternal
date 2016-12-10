from django.conf.urls import url, include
from django.contrib import admin

from ccbrt_mane import views

urlpatterns = [
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout'),
    url(r'^', include('questionnaire.urls')),
    url(r'^admin/', admin.site.urls),
]

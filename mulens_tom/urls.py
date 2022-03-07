"""mulens_tom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.contrib import admin
from tom import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('manage_account/', views.manage_account, name='manage_account'),
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('test/',views.test,name="test"),
    path('project/',views.project,name="project"),
    path('targets/',views.targets,name="targets"),
    path('add_target/',views.add_target,name="add_target"),
    path('remove_target/',views.remove_target,name="remove_target"),
    path('observations/',views.observations,name="observations"),
    path('request_obs/',views.request_obs,{'obs_type':'multi-site'},name="request_obs"),
    path('request_obs/multisite/',views.request_obs,{'obs_type':'multi-site'},name="request_multisite_obs"),
    path('request_obs/singlesite/',views.request_obs,{'obs_type':'single-site'},name="request_singlesite_obs"),
    path('send_test_email/',views.send_test_email,name="test_email"),
]

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
from django.conf.urls import url
from django.contrib import admin
from tom.views import home, targets, add_target, observations, request_obs
from tom.views import manage_account, change_password, test, send_test_email
from tom.views import project, remove_target
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name':'tom/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page':'/'}, name='logout'),
    url(r'^change_password/$', change_password, name='change_password'),
    url(r'^manage_account/$', manage_account, name='manage_account'),
    url(r'^admin/', admin.site.urls),
    url(r'^$',home,name="home"),
    url(r'^test/$',test,name="test"),
    url(r'^project/$',project,name="project"),
    url(r'^targets/$',targets,name="targets"),
    url(r'^add_target/$',add_target,name="add_target"),
    url(r'^remove_target/$',remove_target,name="remove_target"),
    url(r'^observations/$',observations,name="observations"),
    url(r'^request_obs/$',request_obs,{'obs_type':'multi-site'},name="request_obs"),
    url(r'^request_obs/multisite/$',request_obs,{'obs_type':'multi-site'},name="request_multisite_obs"),
    url(r'^request_obs/singlesite/$',request_obs,{'obs_type':'single-site'},name="request_singlesite_obs"),
    url(r'^send_test_email/$',send_test_email,name="test_email"),
]

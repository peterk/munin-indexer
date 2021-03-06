"""muninweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from munin import views
import munin.jobs
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.index),
    path('chart_script.js', views.chart_script),
    path('bulk_add/', views.bulk_add),
    path('collection_meta/<int:collection_id>', views.collection_meta),
    path('admin/', admin.site.urls),
    path('seeds/<int:seed_id>/', views.add_post_url_for_seed),
    path('add_post/', views.add_post_url),
    path('dequeue_seed/', views.dequeue_seed),
    path('dequeue_post/', views.dequeue_post_url),
    path('export_seed_data/', views.export_seed_data),
]

"""candy_delivery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path, re_path

from candy_delivery.delivery.views import *

urlpatterns = [
    # path('admin/', admin.site.urls),

    re_path(r'couriers/?$', add_couriers),
    re_path(r'couriers/(?P<courier_id>\d+)\/?$', CouriersView.as_view()),

    re_path(r'orders/?$', add_orders),
    re_path(r'orders/assign\/?$', assign_orders),
    re_path(r'orders/complete\/?$', complete_order),
]

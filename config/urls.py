"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from .graphql_view import CustomGraphQLView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', CustomGraphQLView.as_view(), name='graphql'),
    path('api/products/', include('apps.product.urls')),
    path('api/suppliers/', include('apps.supplier.urls')),
    path('api/purchases/', include('apps.purchase.urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
]

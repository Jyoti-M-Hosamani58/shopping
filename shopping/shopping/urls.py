"""
URL configuration for shopping project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from shopping_app import views

from django.conf import settings
from django.conf.urls.static import static
from shopping_app import views as pwa_views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('admin/', admin.site.urls),

    path('offline/', cache_page(settings.PWA_APP_NAME)(pwa_views.OfflineView.as_view())),

    path('',views.login,name='login'),
    path('logout',views.logout,name='logout'),

    path('admin_home',views.admin_home,name='admin_home'),
    path('staff_home',views.staff_home,name='staff_home'),

    path('addItem',views.addItem,name='addItem'),
    path('viewItem',views.viewItem,name='viewItem'),
    path('editItem/<str:pk>',views.editItem,name='editItem'),
    path('get_item',views.get_item,name='get_item'),

    path('sales',views.sales,name='sales'),
    path('get_item_by_barcode/<str:barcode>/', views.get_item_by_barcode, name='get_item_by_barcode'),
    path('save_sales',views.save_sales,name='save_sales'),
    path('printInvoice/<str:invoice_no>/', views.printInvoice, name='printInvoice'),

    path('viewSales',views.viewSales,name='viewSales'),

    path('returnSale',views.returnSale,name='returnSale'),
    path('save_return',views.save_return,name='save_return'),
    path('get_item_barcode_return/<str:bill>/<str:barcode>/', views.get_item_barcode_return, name='get_item_barcode_return'),

    path('purchaseReport',views.purchaseReport,name='purchaseReport'),
    path('returnReport',views.returnReport,name='returnReport'),

    path('deleteItem/<int:pk>',views.deleteItem,name='deleteItem'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
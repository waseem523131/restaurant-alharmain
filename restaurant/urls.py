from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('ratings/', views.ratings, name='ratings'),
    path(
        'testimonials/',
        RedirectView.as_view(pattern_name='ratings', permanent=True),
    ),
    path('delivery/', views.delivery, name='delivery'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('contact/', views.contact, name='contact'),
]

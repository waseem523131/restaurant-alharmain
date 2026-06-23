from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),

    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('orders/<int:pk>/ajax/', views.ajax_update_order, name='order_ajax'),

    path('dishes/', views.DishListView.as_view(), name='dishes'),
    path('dishes/add/', views.DishCreateView.as_view(), name='dish_add'),
    path('dishes/<int:pk>/edit/', views.DishUpdateView.as_view(), name='dish_edit'),
    path('dishes/<int:pk>/delete/', views.dish_delete, name='dish_delete'),
    path('dishes/<int:pk>/toggle/', views.ajax_toggle_dish, name='dish_toggle'),

    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),

    path('reviews/', views.ReviewListView.as_view(), name='reviews'),
    path('reviews/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('reviews/<int:pk>/toggle/', views.ajax_toggle_review, name='review_toggle'),

    path('messages/', views.MessageListView.as_view(), name='messages'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/toggle/', views.ajax_toggle_message_read, name='message_toggle'),

    path('reservations/', views.ReservationListView.as_view(), name='reservations'),
    path('reservations/<int:pk>/ajax/', views.ajax_update_reservation, name='reservation_ajax'),

    path('payments/', views.PaymentAccountListView.as_view(), name='payments'),
    path('payments/add/', views.PaymentAccountCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/edit/', views.PaymentAccountUpdateView.as_view(), name='payment_edit'),
]

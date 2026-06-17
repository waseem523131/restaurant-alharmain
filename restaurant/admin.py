from django.contrib import admin

from .models import Category, ContactMessage, DeliveryOrder, Dish, Reservation, Testimonial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'is_available', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_featured']
    date_hierarchy = 'created_at'


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'phone', 'item_name', 'quantity',
        'total_amount', 'created_at',
    ]
    list_filter = ['created_at']
    search_fields = ['name', 'phone', 'item_name', 'address']
    readonly_fields = [
        'item_name', 'unit_price', 'delivery_fee',
        'total_amount', 'created_at',
    ]
    date_hierarchy = 'created_at'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'date', 'time', 'persons', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['name', 'phone', 'email']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating', 'position', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['customer_name', 'content']
    list_editable = ['is_active']
    readonly_fields = ['created_at']

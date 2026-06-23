from django.contrib import admin

from .models import (
    Category,
    ContactMessage,
    DeliveryOrder,
    Dish,
    PaymentAccount,
    Reservation,
    Testimonial,
)


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


@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = ['method', 'account_number', 'account_name', 'is_active']
    list_filter = ['is_active', 'method']
    list_editable = ['is_active']
    search_fields = ['account_number', 'account_name']


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'phone',
        'item_name',
        'quantity',
        'total_amount',
        'payment_method',
        'transaction_id',
        'payment_status',
        'order_status',
        'created_at',
    ]
    list_filter = ['order_status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['name', 'phone', 'item_name', 'address', 'transaction_id']
    list_editable = ['payment_status', 'order_status']
    readonly_fields = [
        'item_name',
        'unit_price',
        'delivery_fee',
        'total_amount',
        'created_at',
    ]
    fieldsets = (
        ('بيانات العميل', {
            'fields': ('name', 'phone', 'address'),
        }),
        ('تفاصيل الطلب', {
            'fields': (
                'dish', 'item_name', 'quantity', 'notes',
                'unit_price', 'delivery_fee', 'total_amount',
            ),
        }),
        ('الدفع', {
            'fields': ('payment_method', 'transaction_id', 'payment_status'),
        }),
        ('حالة الطلب', {
            'fields': ('order_status', 'created_at'),
        }),
    )
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

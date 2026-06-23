from django import forms

from restaurant.models import (
    Category,
    ContactMessage,
    DeliveryOrder,
    Dish,
    PaymentAccount,
    Reservation,
    Testimonial,
)


class DashboardFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = f'form-check-input {css}'.strip()
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = f'form-select {css}'.strip()
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = f'form-control {css}'.strip()
            else:
                field.widget.attrs['class'] = f'form-control {css}'.strip()


class CategoryForm(DashboardFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image']
        labels = {
            'name': 'اسم التصنيف',
            'slug': 'الرابط',
            'image': 'الصورة',
        }


class DishForm(DashboardFormMixin, forms.ModelForm):
    class Meta:
        model = Dish
        fields = [
            'name', 'description', 'price', 'image', 'category',
            'is_available', 'is_featured', 'ingredients',
        ]
        labels = {
            'name': 'اسم الطبق',
            'description': 'الوصف',
            'price': 'السعر',
            'image': 'الصورة',
            'category': 'التصنيف',
            'is_available': 'متاح',
            'is_featured': 'مميز',
            'ingredients': 'المكونات',
        }


class TestimonialForm(DashboardFormMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['customer_name', 'customer_image', 'position', 'content', 'rating', 'is_active']
        labels = {
            'customer_name': 'اسم العميل',
            'customer_image': 'صورة العميل',
            'position': 'المنصب',
            'content': 'التعليق',
            'rating': 'التقييم',
            'is_active': 'نشط',
        }


class PaymentAccountForm(DashboardFormMixin, forms.ModelForm):
    class Meta:
        model = PaymentAccount
        fields = ['method', 'account_number', 'account_name', 'qr_code', 'is_active']
        labels = {
            'method': 'طريقة الدفع',
            'account_number': 'رقم الحساب',
            'account_name': 'اسم الحساب',
            'qr_code': 'رمز QR',
            'is_active': 'نشط',
        }


class DeliveryOrderUpdateForm(DashboardFormMixin, forms.ModelForm):
    class Meta:
        model = DeliveryOrder
        fields = ['order_status', 'payment_status', 'transaction_id']
        labels = {
            'order_status': 'حالة الطلب',
            'payment_status': 'حالة الدفع',
            'transaction_id': 'رقم العملية',
        }


class ReservationUpdateForm(DashboardFormMixin, forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['status']
        labels = {'status': 'حالة الحجز'}


class OrderFilterForm(forms.Form):
    q = forms.CharField(required=False, label='بحث')
    order_status = forms.ChoiceField(
        required=False,
        label='حالة الطلب',
        choices=[('', 'الكل')] + list(DeliveryOrder.OrderStatus.choices),
    )
    payment_status = forms.ChoiceField(
        required=False,
        label='حالة الدفع',
        choices=[('', 'الكل')] + list(DeliveryOrder.PaymentStatus.choices),
    )

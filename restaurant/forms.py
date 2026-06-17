from django import forms

from .models import ContactMessage, DeliveryOrder, Testimonial
from .utils import CLOSED_MESSAGE, is_restaurant_open


class DeliveryOrderForm(forms.ModelForm):
    class Meta:
        model = DeliveryOrder
        fields = ['name', 'phone', 'address', 'quantity', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسمك الكامل',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '77xxxxxxx',
                'pattern': r'^[0-9]{9,15}$',
                'title': 'أدخل رقم جوال صحيح',
                'required': True,
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل عنوان التوصيل بالتفصيل',
                'required': True,
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 99,
                'value': 1,
                'required': True,
                'id': 'id_quantity',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات على الطلب (اختياري)',
            }),
        }
        labels = {
            'name': 'الاسم الكامل',
            'phone': 'رقم الجوال',
            'address': 'عنوان التوصيل',
            'quantity': 'الكمية',
            'notes': 'ملاحظات على الطلب',
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity < 1:
            raise forms.ValidationError('يجب أن تكون الكمية 1 على الأقل.')
        if quantity and quantity > 99:
            raise forms.ValidationError('الحد الأقصى للكمية 99.')
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        if not is_restaurant_open():
            raise forms.ValidationError(CLOSED_MESSAGE)
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسمك',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع الرسالة',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'اكتب رسالتك هنا...',
                'required': True,
            }),
        }
        labels = {
            'name': 'الاسم',
            'email': 'البريد الإلكتروني',
            'subject': 'الموضوع',
            'message': 'الرسالة',
        }


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        coerce=int,
        empty_value=None,
        widget=forms.RadioSelect(attrs={'class': 'star-radio-input'}),
        label='التقييم',
        error_messages={'required': 'يرجى اختيار التقييم بالنجوم.'},
    )

    class Meta:
        model = Testimonial
        fields = ['customer_name', 'rating', 'content']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسمك',
                'required': True,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب تعليقك أو ملاحظتك هنا...',
                'required': True,
            }),
        }
        labels = {
            'customer_name': 'الاسم',
            'content': 'التعليق أو الملاحظة',
        }

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise forms.ValidationError('الاسم مطلوب.')
        return name

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('يرجى كتابة تعليقك.')
        return content

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError('يرجى اختيار التقييم بالنجوم.')
        return int(rating)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.position = 'عميل'
        instance.is_active = True
        if commit:
            instance.save()
        return instance

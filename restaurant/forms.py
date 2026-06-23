from django import forms

from .models import ContactMessage, DeliveryOrder, Testimonial


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


class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=DeliveryOrder.PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        label='طريقة الدفع',
        error_messages={'required': 'يرجى اختيار طريقة الدفع.'},
    )
    transaction_id = forms.CharField(
        required=False,
        label='رقم العملية',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل رقم العملية بعد التحويل',
            'id': 'id_transaction_id',
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        transaction_id = (cleaned_data.get('transaction_id') or '').strip()

        if DeliveryOrder.is_electronic_method(payment_method) and not transaction_id:
            self.add_error(
                'transaction_id',
                'يرجى إدخال رقم العملية بعد إتمام التحويل.',
            )

        cleaned_data['transaction_id'] = transaction_id
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

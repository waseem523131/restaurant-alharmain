from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField('التصنيف', max_length=100)
    slug = models.SlugField('الرابط', unique=True, max_length=100)
    image = models.ImageField('الصورة', upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Dish(models.Model):
    name = models.CharField('اسم الطبق', max_length=200)
    description = models.TextField('الوصف')
    price = models.DecimalField('السعر', max_digits=8, decimal_places=2)
    image = models.ImageField('الصورة', upload_to='dishes/')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name='التصنيف',
    )
    is_available = models.BooleanField('متاح', default=True)
    is_featured = models.BooleanField('مميز', default=False)
    ingredients = models.TextField('المكونات', blank=True)
    is_deleted = models.BooleanField('محذوف', default=False)
    deleted_at = models.DateTimeField('تاريخ الحذف', blank=True, null=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'طبق'
        verbose_name_plural = 'الأطباق'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PaymentAccount(models.Model):
    class Method(models.TextChoices):
        KARIMI = 'karimi', 'كريمي جوال'
        JEIB = 'jeib', 'جيب'
        KASH = 'kash', 'كاش'

    method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=Method.choices,
        unique=True,
    )
    account_number = models.CharField('رقم الحساب', max_length=50)
    account_name = models.CharField('اسم الحساب', max_length=100, blank=True)
    qr_code = models.ImageField('رمز QR', upload_to='payment_qr/', blank=True, null=True)
    is_active = models.BooleanField('نشط', default=True)

    class Meta:
        verbose_name = 'حساب دفع إلكتروني'
        verbose_name_plural = 'حسابات الدفع الإلكتروني'

    def __str__(self):
        return self.get_method_display()


class DeliveryOrder(models.Model):
    class PaymentMethod(models.TextChoices):
        COD = 'cod', 'الدفع عند الاستلام'
        KARIMI = 'karimi', 'كريمي جوال'
        JEIB = 'jeib', 'جيب'
        KASH = 'kash', 'كاش'

    class OrderStatus(models.TextChoices):
        PENDING_REVIEW = 'pending_review', 'قيد المراجعة'
        CONFIRMED = 'confirmed', 'تم التأكيد'
        DELIVERED = 'delivered', 'تم التوصيل'
        CANCELLED = 'cancelled', 'ملغي'

    class PaymentStatus(models.TextChoices):
        UNCONFIRMED = 'unconfirmed', 'غير مؤكد'
        PAID = 'paid', '\u0645\u062f\u0641\u0648\u0639'

    ELECTRONIC_METHODS = {
        PaymentMethod.KARIMI,
        PaymentMethod.JEIB,
        PaymentMethod.KASH,
    }

    name = models.CharField('الاسم الكامل', max_length=100)
    phone = models.CharField('رقم الجوال', max_length=20)
    address = models.TextField('عنوان التوصيل')
    dish = models.ForeignKey(
        Dish,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_orders',
        verbose_name='الطبق',
    )
    item_name = models.CharField('اسم الصنف', max_length=200)
    quantity = models.PositiveIntegerField('الكمية', default=1)
    notes = models.TextField('ملاحظات على الطلب', blank=True)
    unit_price = models.DecimalField('سعر الصنف', max_digits=8, decimal_places=2)
    delivery_fee = models.DecimalField('رسوم التوصيل', max_digits=8, decimal_places=2)
    total_amount = models.DecimalField('المبلغ الإجمالي', max_digits=8, decimal_places=2)
    payment_method = models.CharField(
        'طريقة الدفع',
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )
    transaction_id = models.CharField('رقم العملية', max_length=100, blank=True)
    order_status = models.CharField(
        'حالة الطلب',
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_REVIEW,
    )
    payment_status = models.CharField(
        'حالة الدفع',
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNCONFIRMED,
    )
    is_deleted = models.BooleanField('محذوف', default=False)
    deleted_at = models.DateTimeField('تاريخ الحذف', blank=True, null=True)
    created_at = models.DateTimeField('تاريخ الطلب', auto_now_add=True)

    class Meta:
        verbose_name = 'طلب توصيل'
        verbose_name_plural = 'طلبات التوصيل'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.item_name}'

    @property
    def is_electronic_payment(self):
        return self.payment_method in self.ELECTRONIC_METHODS

    @classmethod
    def is_electronic_method(cls, method):
        return method in cls.ELECTRONIC_METHODS


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        CONFIRMED = 'confirmed', 'مؤكد'
        CANCELLED = 'cancelled', 'ملغي'
        COMPLETED = 'completed', 'مكتمل'

    name = models.CharField('الاسم', max_length=100)
    phone = models.CharField('رقم الجوال', max_length=20)
    email = models.EmailField('البريد الإلكتروني')
    date = models.DateField('التاريخ')
    time = models.TimeField('الوقت')
    persons = models.IntegerField('عدد الأشخاص')
    message = models.TextField('رسالة', blank=True)
    status = models.CharField(
        'حالة الحجز',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.date}'


class ContactMessage(models.Model):
    name = models.CharField('الاسم', max_length=100)
    email = models.EmailField('البريد الإلكتروني')
    subject = models.CharField('الموضوع', max_length=200)
    message = models.TextField('الرسالة')
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    is_read = models.BooleanField('مقروءة', default=False)

    class Meta:
        verbose_name = 'رسالة تواصل'
        verbose_name_plural = 'رسائل التواصل'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} - {self.name}'


class Testimonial(models.Model):
    customer_name = models.CharField('اسم العميل', max_length=100)
    customer_image = models.ImageField('صورة العميل', upload_to='testimonials/', blank=True, null=True)
    position = models.CharField('المنصب', max_length=100, default='عميل')
    content = models.TextField('المحتوى')
    rating = models.IntegerField('التقييم', choices=[(i, str(i)) for i in range(1, 6)])
    is_active = models.BooleanField('نشط', default=True)
    is_deleted = models.BooleanField('محذوف', default=False)
    deleted_at = models.DateTimeField('تاريخ الحذف', blank=True, null=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'
        ordering = ['-created_at']

    def __str__(self):
        return self.customer_name

    @classmethod
    def get_average_rating(cls):
        from django.db.models import Avg

        result = cls.objects.filter(is_active=True, is_deleted=False).aggregate(avg=Avg('rating'))
        if result['avg'] is None:
            return 0
        return round(result['avg'], 1)

    @classmethod
    def get_reviews_count(cls):
        return cls.objects.filter(is_active=True, is_deleted=False).count()

# Generated manually for payment system

from django.db import migrations, models


def create_default_payment_accounts(apps, schema_editor):
    PaymentAccount = apps.get_model('restaurant', 'PaymentAccount')
    defaults = [
        {
            'method': 'karimi',
            'account_number': '77xxxxxxx',
            'account_name': 'مطعم الحرمين',
        },
        {
            'method': 'jeib',
            'account_number': '77xxxxxxx',
            'account_name': 'مطعم الحرمين',
        },
        {
            'method': 'kash',
            'account_number': '77xxxxxxx',
            'account_name': 'مطعم الحرمين',
        },
    ]
    for data in defaults:
        PaymentAccount.objects.get_or_create(method=data['method'], defaults=data)


def remove_default_payment_accounts(apps, schema_editor):
    PaymentAccount = apps.get_model('restaurant', 'PaymentAccount')
    PaymentAccount.objects.filter(method__in=['karimi', 'jeib', 'kash']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_alter_testimonial_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(
                    choices=[('karimi', 'كريمي جوال'), ('jeib', 'جيب'), ('kash', 'كاش')],
                    max_length=20,
                    unique=True,
                    verbose_name='طريقة الدفع',
                )),
                ('account_number', models.CharField(max_length=50, verbose_name='رقم الحساب')),
                ('account_name', models.CharField(blank=True, max_length=100, verbose_name='اسم الحساب')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='payment_qr/', verbose_name='رمز QR')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
            ],
            options={
                'verbose_name': 'حساب دفع إلكتروني',
                'verbose_name_plural': 'حسابات الدفع الإلكتروني',
            },
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='order_status',
            field=models.CharField(
                choices=[
                    ('pending_review', 'قيد المراجعة'),
                    ('confirmed', 'تم التأكيد'),
                    ('delivered', 'تم التوصيل'),
                    ('cancelled', 'ملغي'),
                ],
                default='pending_review',
                max_length=20,
                verbose_name='حالة الطلب',
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cod', 'الدفع عند الاستلام'),
                    ('karimi', 'كريمي جوال'),
                    ('jeib', 'جيب'),
                    ('kash', 'كاش'),
                ],
                default='cod',
                max_length=20,
                verbose_name='طريقة الدفع',
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='payment_status',
            field=models.CharField(
                choices=[('unconfirmed', 'غير مؤكد'), ('paid', '\u0645\u062f\u0641\u0648\u0639')],
                default='unconfirmed',
                max_length=20,
                verbose_name='حالة الدفع',
            ),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='رقم العملية'),
        ),
        migrations.RunPython(create_default_payment_accounts, remove_default_payment_accounts),
    ]

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'إنشاء مستخدم مدير للوحة التحكم (بدون Render Shell)'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING(f'تم تحديث المستخدم: {username}'))
        else:
            User.objects.create_superuser(username=username, password=password, email='')
            self.stdout.write(self.style.SUCCESS(f'تم إنشاء المدير: {username}'))

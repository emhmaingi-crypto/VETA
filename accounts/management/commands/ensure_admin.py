import os
import re
from django.core.management.base import BaseCommand
from accounts.models import StudentUser


class Command(BaseCommand):
    help = 'Create or reset the superuser from ADMIN_EMAIL / ADMIN_PASSWORD env vars'

    def handle(self, *args, **options):
        email = os.environ.get('ADMIN_EMAIL', '').strip()
        password = os.environ.get('ADMIN_PASSWORD', '').strip()

        if not email or not password:
            self.stdout.write('ADMIN_EMAIL or ADMIN_PASSWORD not set — skipping ensure_admin.')
            return

        user = StudentUser.objects.filter(email__iexact=email).first()
        if user:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save(update_fields=['password', 'is_staff', 'is_superuser', 'is_active'])
            self.stdout.write(self.style.SUCCESS(f'Admin updated: {email} (username: {user.username})'))
        else:
            base = re.sub(r'[^a-zA-Z0-9]', '', email.split('@')[0])[:20] or 'admin'
            username = base
            counter = 1
            while StudentUser.objects.filter(username=username).exists():
                username = f'{base}{counter}'
                counter += 1
            StudentUser.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='student',
            )
            self.stdout.write(self.style.SUCCESS(f'Admin created: {email} (username: {username})'))

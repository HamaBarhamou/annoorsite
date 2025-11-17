from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Crée un superuser depuis les variables d'env s'il n'existe pas."

    def handle(self, *args, **opts):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not (username and email and password):
            self.stdout.write(
                self.style.WARNING(
                    "ensure_superuser: DJANGO_SUPERUSER_* non définies ; on ignore."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"ensure_superuser: superuser '{username}' créé.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"ensure_superuser: '{username}' existe déjà ; aucun changement."
                )
            )

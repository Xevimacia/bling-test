from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Updates the superuser with an external_id'

    def add_arguments(self, parser):
        parser.add_argument(
            '--external-id',
            type=str,
            help='External ID to set for the superuser',
            default='super_user_id_123'  # Default value if none provided
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the superuser to update',
            default='admin'  # Default to 'admin' if not specified
        )

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['username'], is_superuser=True)
            user.external_id = options['external_id']
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated superuser {user.username} with external_id: {user.external_id}'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'Superuser with username {options["username"]} not found'
                )
            ) 
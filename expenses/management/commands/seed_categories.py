from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from expenses.models import Category

User = get_user_model()

DEFAULT_CATEGORIES = [
    {'name': 'Food', 'icon': 'utensils', 'color': '#f97316'},
    {'name': 'Transport', 'icon': 'car', 'color': '#3b82f6'},
    {'name': 'Rent', 'icon': 'home', 'color': '#8b5cf6'},
    {'name': 'Utilities', 'icon': 'zap', 'color': '#eab308'},
    {'name': 'Entertainment', 'icon': 'film', 'color': '#ec4899'},
    {'name': 'Healthcare', 'icon': 'heart-pulse', 'color': '#ef4444'},
    {'name': 'Shopping', 'icon': 'shopping-bag', 'color': '#14b8a6'},
    {'name': 'Education', 'icon': 'book-open', 'color': '#6366f1'},
    {'name': 'Other', 'icon': 'more-horizontal', 'color': '#64748b'},
]

class Command(BaseCommand):
    help = 'Seeds default categories for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to seed categories for')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist.'))
            return

        created_count = 0
        for cat_data in DEFAULT_CATEGORIES:
            cat, created = Category.objects.get_or_create(
                user=user,
                name=cat_data['name'],
                defaults={'icon': cat_data['icon'], 'color': cat_data['color']}
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} default categories for user "{username}".'))

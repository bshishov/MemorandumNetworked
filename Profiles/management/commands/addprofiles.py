from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from Profiles.models import Profile

class Command(BaseCommand):
    help = 'Creates user profiles if not exist'

    def handle(self, *args, **options):
        print('Checking user profiles...')
        users = User.objects.all()
        for user in users:
            try:
                profile = user.profile
            except:
                node = Node(user=user, text='Home node for user %s' % user.username)
                node.save()
                profile = Profile(user=user, home=node)
                profile.save()
                user.profile = profile
                user.save()
        print('All users now have profile')
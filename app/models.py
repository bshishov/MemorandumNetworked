from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# here will be defined models for home directories,
# info about sharing directories and item-model
class ProfileManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)

        home = Node(user=user, text='...')
        home.save()

        user.home = home
        user.save()
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return Profile.objects.get(email=username)


class Profile(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email address',
        max_length=255,
        unique=True,
    )
    home = models.ForeignKey('app.Node', blank=True, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField("Is active", default=True)
    is_admin = models.BooleanField("Is admin", default=False)
    date_joined = models.DateTimeField("Date joined", auto_now=True)

    objects = ProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_username(self):
        return self.email

    @property
    def username(self):
        return self.email

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Node(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)


class Url(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url_hash = models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    image = models.CharField(max_length=1000, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class Link(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    node1 = models.CharField(max_length=1000)
    node2 = models.CharField(max_length=1000)
    provider1 = models.CharField(max_length=100)
    provider2 = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)
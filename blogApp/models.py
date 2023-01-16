from unicodedata import category
from django.db import models
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    contact = models.CharField(max_length=250)
    dob = models.DateField(blank=True, null = True)
    address = models.TextField(blank=True, null = True)
    avatar = models.ImageField(blank=True, null = True, upload_to= 'images/')
    user_type = models.IntegerField(default = 1)


    def __str__(self):
        return self.user.username
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    print(instance)
    try:
        profile = UserProfile.objects.get(user = instance)
    except Exception as e:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default = 1)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    title = models.TextField()
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    capital = models.TextField(default=500000)
    blog_post = models.TextField()
    banner = models.ImageField(blank=True, null = True, upload_to= 'images/')
    status = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title + " - " + self.category.name

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)
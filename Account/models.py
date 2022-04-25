from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser

# Create your models here.
def img_path(instance,filename):
    return 'profile/{0}/{1}'.format(instance.username,filename)

class User(AbstractUser):
    email=models.EmailField(blank=False,unique=True)
    db=models.DateField(null=True)
    first_name=models.CharField(null=False,max_length=120)
    last_name=models.CharField(null=True,max_length=120)
    gender=models.CharField(max_length=10)
    picture=models.ImageField(upload_to=img_path,default='default/profile.png')
    is_verified=models.BooleanField(default=False)
    
class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    bio=models.CharField(max_length=120,null=True)
    favourite=models.ManyToManyField('Main.Post')
    
    
    #information
    address=models.CharField(max_length=140,null=True)
    quotes=models.CharField(max_length=120,null=True,blank=True)
    #connect
    website=models.CharField(max_length=120,blank=True,null=True)
    twitter=models.CharField(max_length=120,blank=True,null=True)
    instragram=models.CharField(max_length=120,blank=True,null=True)
    facebook=models.CharField(max_length=120,blank=True,null=True)
    github=models.CharField(max_length=120,blank=True,null=True)


    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
           Profile.objects.create(user=instance)

    def __str__(self):
        return self.user.username




     
from django.db import models
from django.conf import settings
from django.db import connection
#from django.contrib.gis.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    lattitude = models.FloatField()
    longitude = models.FloatField()
    continent = models.CharField(max_length=100,default="")
    country_code = models.CharField(max_length=5,default="")
    country = models.CharField(max_length=100,default="")
    state = models.CharField(max_length=100,default="")
    postcode = models.CharField(max_length=10,default="")
    county = models.CharField(max_length=100,default="")
    #geopoint = models.PointField(default="")

# Create your models here.
class Userprofile(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_name = models.CharField(max_length=100)
    location = models.ForeignKey(Location,null=True,blank=True,on_delete=models.CASCADE)
    dp = models.ImageField(upload_to='dp',null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)

class Post(models.Model):
    image = models.ImageField(upload_to='posts')
    caption = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    location = models.CharField(max_length = 200,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True)
    # def save(self, request):
    #     self.user = request.user
    #     super().save()

class Likes(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    read_by_owner = models.BooleanField(default=False)

class Comment(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post,on_delete=models.CASCADE)
    comment_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    read_by_owner = models.BooleanField(default=False)
    parent_comment_id = models.ForeignKey('self',null=True,blank=True, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    read_by_owner = models.BooleanField(default=False)

class Follow(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    follower_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_follower',on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

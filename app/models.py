from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User 
# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,unique=True)

    def save(self,*args,**kwargs):
        if not self.id:
            self.slug=slugify(self.name)
        return super(Tag,self).save(*args,**kwargs)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=200,unique=True)
    image = models.ImageField(null=True,blank=True,upload_to='images/')
    tags = models.ManyToManyField(Tag,blank=True,related_name='post')
    view_count = models.IntegerField(null=True,blank=True)
    is_featured = models.BooleanField(default=False)
    author = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    bookmarks  = models.ManyToManyField(User,default=None,blank=True,related_name='bookmarks')
    likes = models.ManyToManyField(User,default=None,blank=True,related_name='post_like')

    def number_of_likes(self):
        return self.likes.count()

class Comment(models.Model):
    content=models.TextField()
    date=models.DateField(auto_now=True)
    name=models.CharField(max_length=200)
    email=models.EmailField(max_length=200)
    website=models.CharField(max_length=200)
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    author=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    parent=models.ForeignKey('self',on_delete=models.DO_NOTHING,null=True,blank=True,related_name='replies')

class Subscribe(models.Model):
    email = models.EmailField(max_length=100)
    date = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile_image = models.ImageField(null=True,blank=True,upload_to="images/")
    slug = models.SlugField(max_length=200,unique=True)
    bio = models.CharField(max_length=200)

    def save(self,*args,**kwargs):
        if not self.id:
            self.slug = slugify(self.user.username)
        return super(Profile,self).save(*args,**kwargs)
    
    def __str__(self):
        return self.user.first_name
    
class WebsiteMeta(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    about = models.TextField()
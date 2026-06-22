from django.db import models
from account.models import User
# Create your models here.





class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post" , null=True)
    title = models.CharField(max_length=200)
    category = models.ManyToManyField(Category, blank=True, related_name = "post")
    content = models.TextField()
    image = models.ImageField(upload_to="media/img", null=True, blank=True)
    active= models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default = 0)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "like")
    post = models.ForeignKey(Post, models.CASCADE, related_name='like')
    created = models.DateTimeField(auto_now_add = True)    
    def __str__(self):
        return f"{self.user}, {self.post}"
    
class Comment(models.Model):
    parent = models.ForeignKey('self', on_delete= models.CASCADE, related_name = 'reply', null=True, blank=True)
    post = models.ForeignKey(Post, models.CASCADE, related_name = 'comment')
    user = models.ForeignKey(User, models.CASCADE, related_name = 'user', null=True)
    body = models.TextField()

    def __str__(self):
        return self.user
    

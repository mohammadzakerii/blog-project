from django.test import TestCase
from .models import Category, Post, Comment, Like
from account.models import User
from django.urls import reverse
import json

# Create your tests here.

class CategoryTest(TestCase):
    def setUp(self):
        self.instance  = Category.objects.create(name='books')
        self.admin_user =User.objects.create_superuser(phone="09121231234", password="123456789", fullname="mohammadzakeri") 

    def test_category(self):
        response = self.client.get(reverse('category'))
        self.assertEqual(response.status_code, 200) 

    def test_create_category(self):
        data={
            "name":"cars"
        }      
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('category'), data =json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

class CategoryDetailTest(TestCase):
    def setUp(self):
        self.instance  = Category.objects.create(name='books')
        self.admin_user =User.objects.create_superuser(phone="09121231234", password="123456789", fullname="mohammadzakeri") 
    def test_category_detail(self):
        response = self.client.get(reverse('category_detail', kwargs={'pk':self.instance.id}))
        self.assertEqual(response.status_code, 200)

    def test_category_update(self):
        data={
            "name":"motorbike"
        }
        self.client.force_login(self.admin_user)
        response= self.client.put(reverse('category_detail', kwargs={'pk':self.instance.id}), data=json.dumps(data), content_type='application/json')  
        self.assertEqual(response.status_code, 200) 

    def test_category_delete(self):
        self.client.force_login(self.admin_user)
        response = self.client.delete(reverse('category_detail', kwargs={"pk":self.instance.id})) 
        self.assertEqual(response.status_code, 200)  

class PostTest(TestCase):
    def setUp(self):
        self.category_obj = Category.objects.create(name="books")
        self.post_obj = Post.objects.create(title="meaning of life", content="this post is about how to live to feel like youre happy")
        self.post_obj.category.set([self.category_obj])
        self.admin_user = User.objects.create_superuser(phone="09123456789", password = "123456789", fullname="mohammadzakeri")
        self.normal_user = User.objects.create_user(phone="09121234567", password = "123456789", fullname="aliakbari")
    def test_post(self):
        response = self.client.get(reverse("post"))
        self.assertEqual(response.status_code, 200)           

    def test_create_post(self):
        data={
        "title":"a new book written by chals duek",
        "content":"this book is about how to change you mindset to be a more effective person",
        "active":True,
        "author":self.admin_user}
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("post"), data=data)
        self.assertEqual(response.status_code, 201)


class PostDetailTest(TestCase):
    def setUp(self):
        self.category_obj = Category.objects.create(name="books")
        self.post_obj = Post.objects.create(title="meaning of life", content="this post is about how to live to feel like youre happy")
        self.post_obj.category.set([self.category_obj])
        self.admin_user = User.objects.create_superuser(phone="09123456789", password = "123456789", fullname="mohammadzakeri")
        self.normal_user = User.objects.create_user(phone="09121234567", password = "123456789", fullname="aliakbari")
    def test_postdetail_update(self):
        data={
            "title":"the combined effect",
            "content":"to do small task every day consistantly",
            "active":True,
            "author":self.admin_user.id
        }
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('post_detail', kwargs={"pk":self.post_obj.id}), data=data)
        self.assertEqual(response.status_code, 300)

    def test_postdetail_delete(self):
        self.client.force_login(self.admin_user) 
        response = self.client.delete(reverse('post_detail', kwargs={"pk":self.post_obj.id}))
        self.assertEqual(response.status_code, 200) 


class CommentAndReplyTest(TestCase) :
    def setUp(self):
        
        self.admin_user = User.objects.create_superuser(phone="09123456789", password = "123456789", fullname="mohammadzakeri")
        self.normal_user = User.objects.create_user(phone="09121234567", password = "123456789", fullname="aliakbari")
        self.normal_user2 = User.objects.create_user(phone="09135798641", password="123456789", fullname="ahmad ahmadi")
        self.category_obj = Category.objects.create(name="books")
        self.post_obj = Post.objects.create(title="meaning of life", content="this post is about how to live to feel like youre happy")
        self.post_obj.category.set([self.category_obj])
        self.comment_obj = Comment.objects.create(body="such a great book it is", post_id=self.post_obj.id, user_id=self.normal_user.id, parent=None)
        self.comment_reply = Comment.objects.create(body="yes I like one too thank you" ,parent_id=self.comment_obj.id, post_id = self.post_obj.id, user_id = self.normal_user2.id )
    def test_comments(self):
        response = self.client.get(reverse("comment_post", kwargs={'pk':self.post_obj.id}))
        self.assertEqual(response.status_code, 200)    

    def test_comment(self):
        data={
            "body":"i like to study this book"
        }
        self.client.force_login(self.normal_user)
        response = self.client.post(reverse("comment_post", kwargs={"pk":self.post_obj.id}), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_comment_detail(self):
        response = self.client.get(reverse("comment_detail", kwargs={'pk':self.comment_obj.id}))
        self.assertEqual(response.status_code, 200)

    def test_comment_detail(self):
        data={
        'body':'I really want to buy this interesting book'
            }

        self.client.force_login(self.admin_user)
        response = self.client.put(reverse("comment_detail", kwargs={'pk':self.comment_obj.id}), data=json.dumps(data), content_type= "application/json")
        self.assertEqual(response.status_code, 201)    

    def test_comment_delete(self):
        self.client.force_login(self.normal_user)
        response = self.client.delete(reverse("comment_detail", kwargs={'pk':self.comment_obj.id}))
        self.assertEqual(response.status_code, 200)

    def test_replies_one_comment_retrive(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse("reply_comment", kwargs={'pk':self.comment_obj.id}))
        self.assertEqual(response.status_code, 200)

    def test_create_reply(self):
        data={
            "body":"i agree with you"
        }
        self.client.force_login(self.normal_user2)
        response = self.client.post(reverse("reply_comment", kwargs={'pk':self.comment_obj.id}), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)  


class LikeTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(phone="09123456789", password = "123456789", fullname="mohammadzakeri")
        self.normal_user = User.objects.create_user(phone="09121234567", password = "123456789", fullname="aliakbari")
        self.normal_user2 = User.objects.create_user(phone="09135798641", password="123456789", fullname="ahmad ahmadi")
        self.category_obj = Category.objects.create(name="books")
        self.post_obj = Post.objects.create(title="meaning of life", content="this post is about how to live to feel like youre happy")
        self.post_obj.category.set([self.category_obj])
        self.comment_obj = Comment.objects.create(body="such a great book it is", post_id=self.post_obj.id, user_id=self.normal_user.id, parent=None)
        self.comment_reply = Comment.objects.create(body="yes I like one too thank you" ,parent_id=self.comment_obj.id, post_id = self.post_obj.id, user_id = self.normal_user2.id )
        self.like_obj = Like.objects.create(post=self.post_obj, user=self.normal_user)
        self.post_obj.like_count += 1
        self.post_obj.save()

    def test_get_likes(self):
        response = self.client.get(reverse("likes", kwargs={"pk":self.post_obj.id}))
        self.assertEqual(response.status_code, 200)

    def test_create_or_delete_like(self):
        self.client.force_login(self.normal_user)
        response = self.client.post(reverse("create_delete_like", kwargs={'pk':self.post_obj.id}))
        self.assertEqual(response.status_code, 200)    






            
        

              








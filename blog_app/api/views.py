from blog_app.models import Category, Comment, Like,Post
from account.models import Profile
from account.models import User
from django.http import JsonResponse
from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.core.paginator import Paginator


@method_decorator(csrf_exempt, name="dispatch")
class CategpryView(View):
    def get(self, request):
        category = Category.objects.all()
        data = [{"id":c.id,"category_name":c.name, "created_at":c.created}for c in category]
        return JsonResponse({"categories":data}, status=200)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        elif not request.user.is_staff:
            return JsonResponse({"error":"you dont have permission"}, status=403) 
        
        data = json.loads(request.body)
        name = data.get("name")
        if Category.objects.filter(name=name).exists():
            return JsonResponse({"error":f"the category name {name} has been created befor"}, status=400)
        category_obj = Category.objects.create(name=name)
        return JsonResponse({"message":"category created successfully","name":name, "created":category_obj.created}, status=201)

@method_decorator(csrf_exempt, name="dispatch")
class Category_Detail(View):
    def get(self, request, pk):
        try:
            category_obj = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return JsonResponse({"error":"category with this id doesnt exists"}, status=404) 

        return JsonResponse({"name":category_obj.name, "created":category_obj.created})   

    def put(self, request, pk):
        
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        elif not request.user.is_staff:
            return JsonResponse({"error":"you dont have permission"}, status=403)  
        try:
            category_obj = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return JsonResponse({"error":"category with this id doesnt exists"}, status=404) 

        data = json.loads(request.body)
        name= data.get("name", category_obj.name)
        if Category.objects.filter(name=name).exists():
            return JsonResponse({"error":"not unique category name"}, status=400)
        category_obj.name = name
        category_obj.save()
        return JsonResponse({"message":"updated successfully", "category_name":category_obj.name}, status=200)
    
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        elif not request.user.is_staff:
            return JsonResponse({"error":"you dont have permission"}, status=403) 
        try:
            category_obj = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return JsonResponse({"error":"category object not found"}, status=404) 
        
        category_obj.delete()
        return JsonResponse({"message":"deleted successfully"}, status=200)
    
@method_decorator(csrf_exempt, name="dispatch")
class PostView(View):
    def get(self, request):
        post_obj = Post.objects.all()
        category_list=[]
        for p in post_obj:
            for c in p.category.all():
                data2={"category_id":c.id,"category_name":c.name}
                category_list.append(data2)
                
        data = [{"id":p.id, "title":p.title, "content":p.content, "author":p.author.fullname if p.author else None, "image":p.image.url if p.image else None, "categories":[c.name for c in p.category.all()]}for p in post_obj]
        return JsonResponse({"posts":data}, status=200)

    def post(self,  request):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        elif not request.user.is_staff:
            return JsonResponse({"error":"you dont have permission"}, status=403) 
        title = request.POST.get("title")
        content = request.POST.get("content")
        category = request.POST.getlist("category")
        image = request.FILES.get("image")
        active = request.POST.get("active").lower() == "true"
        current_user = User.objects.get(pk=request.user.id)
        author = current_user
        if Post.objects.filter(title=title, content = content).exists():
            return JsonResponse({"error":"this post already existed"})
       
        post_obj = Post.objects.create(title = title, content = content, image = image , active=active, author=author)
        if category:
            post_obj.category.set(category)


        return JsonResponse({
            "message":"post created successfully",
            "title":post_obj.title, "content":post_obj.content,
            "category":[c.name for c in post_obj.category.all()],
            "image":post_obj.image.url if post_obj.image else None,
            "active":post_obj.active,
            "author":post_obj.author.fullname}, status=201)
    
@method_decorator(csrf_exempt, name="dispatch")    
class PostDetailView(View):
    def get(self, request, pk):
        try:
            post_obj = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"error":"post doesnt exists"}, status=404)
        
        return JsonResponse({
            "id":post_obj.id, "title":post_obj.title,
            "content":post_obj.content ,"author": post_obj.author.fullname,
            "active": post_obj.active, "image": post_obj.image.url if post_obj.image else None,
            "category":[c.name for c in post_obj.category.all()],
            "comments":[{"id":comment.id,"comment":comment.body, "user":comment.user.fullname} for comment in post_obj.comment.all()]})


    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        elif not request.user.is_staff:
            return JsonResponse({"error":"you dont have permission"}, status=403) 
        try:
            post_obj = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"error":"post doesnt exist"}, status=404)
            
        title = request.POST.get("title", post_obj.title)
        content = request.POST.get("content",post_obj.content)
        active = request.POST.get("active", post_obj.active).lower() == "true"
        image = request.FILES.get("image",post_obj.image)
        category = request.POST.getlist("category")
        post_obj.title = title
        post_obj.content=content
        
        post_obj.active = active
        if image:
            post_obj.image = image
       
        if category:
            post_obj.category.set(category)
        
        current_user = User.objects.get(pk=request.user.id)
        post_obj.author = current_user
        
            
        post_obj.save()    
            
        return JsonResponse({
                "message":"post updated successfully",
                "id":post_obj.id,
                "author":post_obj.author.fullname,
                "title":post_obj.title,
                "author":post_obj.author.fullname,
                "content":post_obj.content,
                "active":post_obj.active,
                "image":post_obj.image.url if post_obj.image else None,
                "category":[c.name for c in post_obj.category.all()] }, status = 300)
        
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        elif not request.user.is_staff:
            return JsonResponse({"message":"you dont have permission"},status=304)
        try:
            post_obj= Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"error":"post doesnt exist"}, status=404)
        
        post_obj.delete()
        return JsonResponse({"message":"post deleted successfully"}, status=200)

@method_decorator(csrf_exempt, name="dispatch")                    
class CommentView(View):
    def get(self, request, pk):
        try:
            post_obj = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"error":"post doesnt exist"}, status =404)
        
        comment = Comment.objects.filter(post = post_obj, parent=None).all()
        comment_list = []
        for c in comment:
            data = {"id":c.id, "comment":c.body, "replies":[{"id":r.id, "reply comment":r.body} for r in c.reply.all()]}
            comment_list.append(data)
        return JsonResponse({"comments":comment_list}, status=200)
            
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        try:
            post_obj = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"error":"post not found"}, status=404) 

        if request.user.is_authenticated:
            data = json.loads(request.body)
            body = data.get("body")
            comment_obj = Comment.objects.create(body = body, post_id=pk, user = request.user)
            return JsonResponse({"message":"comment created successfully", "id":comment_obj.id, "comment":comment_obj.body, "post_title":post_obj.title}, status=201)
        else:
            return JsonResponse({"error":"youre not authenticated"}, status=401)
        

@method_decorator(csrf_exempt, name="dispatch")                    
class CommentDetail(View):
    def get(self, request, pk):
        try:
            comment_obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return JsonResponse({"error":"comment doesnt exist"}, status=404)
        replies = []
        for r in comment_obj.reply.all():
            data ={"id":r.id, "body":r.body}
            replies.append(data)
        return JsonResponse({"id":comment_obj.id, "comment":comment_obj.body, "user":comment_obj.user.fullname, "replies":replies})  

    def put(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        try:
            comment_obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return JsonResponse({"error":"comment doesnt exist"}, status=404)
        if comment_obj.user == request.user or request.user.is_staff:
            data = json.loads(request.body)
            body = data.get("body", comment_obj.body)
            comment_obj.body = body
            comment_obj.save()
            return JsonResponse({"message":"comment updated successfully", "id":comment_obj.id, "comment":comment_obj.body, "user":comment_obj.user.fullname, "replies":[{"id": r.id, "reply comment":r.body}for r in comment_obj.reply.all()]}, status=201)
        else:
            return JsonResponse({"message":"you dont have permission to update this comment"}, status=403)    

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        try:
            comment_obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return JsonResponse({"error":"comment not found"}, status=404)
        if self.request.user ==  comment_obj.user or  request.user.is_staff:
            comment_obj.delete()
            return JsonResponse({"message":"comment deleted successfully"}, status=200)
        else:
            return JsonResponse({"error":"comment user or admin can delete comments"}, status=403)
        
@method_decorator(csrf_exempt, name="dispatch")                            
class ReplyComment(View):

    def get(self, requst, pk):
        try:
            comment_obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return JsonResponse({"error":"parent comment not found"}, status=404)

        reply_comments = Comment.objects.filter(parent = comment_obj).all()
        reply_list=[]
        for reply in reply_comments:
            data = {"id":reply.id, "comment":reply.body, "user":reply.user.fullname}
            reply_list.append(data)
        return JsonResponse({"reply comments":reply_list}, status=200)    

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"message":"not authenticated"}, status=401)
        try:
            comment_obj = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return JsonResponse({"error":"comment dosnt exist"}, status=404)
        
        data = json.loads(request.body)
        body = data.get("body")
        reply_comment = Comment.objects.create(body=body,parent = comment_obj, user= request.user, post=comment_obj.post)
        return JsonResponse({
            "message":"reply created successfully", 
            "id":reply_comment.id, "reply content":reply_comment.body,
            "post title":comment_obj.post.title,
            "parent comment":comment_obj.body}, status=201)
       
        
    

class like(View):
    def get(self, request ,pk):
        try:
            Post_obj = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"message":"post doesnt exist"}, status=404)

        post_likes = Like.objects.filter(post=Post_obj).all()
        like_list=[]
        for l in post_likes:
            data={"id":l.id, "post":l.post.title, "user":l.user.fullname, }
            like_list.append(data)

        return JsonResponse({"likes":like_list, "quentity of like":Post_obj.like_count})

@method_decorator(csrf_exempt, name="dispatch")                              
class CreateOrDeleteLike(View):
    def post(self, request, pk):
        try:
            post_obj = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return JsonResponse({"error": "post doesnt exists"}, status= 404)    
        
        
        if request.user.is_authenticated:
            post_obj.refresh_from_db()
            liked =Like.objects.filter(post=post_obj, user = request.user)
            if liked.exists():
                liked.delete()
                
                post_obj.like_count= F('like_count') - 1
                post_obj.save(update_fields=['like_count'])
                return JsonResponse({"liked":False, "message":"unliked", "quentity of like":f"{post_obj.like_count}"}, status=200)
            else:
                Like.objects.create(post=post_obj, user=request.user)
                post_obj.like_count = F('like_count') + 1
                post_obj.save(update_fields=['like_count'])
                return JsonResponse({"liked":True, "mesasge":"liked","quentity of like":f"{post_obj.like_count}"}, status= 200)
        else:
            return JsonResponse({"error":"not authenticated"}, status=401)    



def search(request):
    query = request.GET.get('search')
    if not query:
        return JsonResponse({"result":None})
    results = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    paginator = Paginator(results, 1)
    page_number = request.GET.get("page")
    page_obj =paginator.get_page(page_number) 
    post_list = []

    for post in page_obj:
        data={"title":post.title, "content":post.content}
        post_list.append(data)
    return JsonResponse({"results":post_list}, status=200)    
    



          
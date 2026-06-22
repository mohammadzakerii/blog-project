from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.CategpryView.as_view(), name="category"),
    path('category/detail/<int:pk>/', views.Category_Detail.as_view(), name="category_detail"),
    path('post/', views.PostView.as_view(), name='post'),
    path("post_detail/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("comment_post/<int:pk>/", views.CommentView.as_view(), name="comment_post"),
    path("comment_detail/<int:pk>/", views.CommentDetail.as_view(), name="comment_detail"),
    path("reply_comment/<int:pk>/", views.ReplyComment.as_view(), name="reply_comment"),
    path("likes/list/<int:pk>/", views.like.as_view(), name="likes"),
    path("like/<int:pk>/", views.CreateOrDeleteLike.as_view(), name="create_delete_like"),
    path("search/", views.search, name="search")
    
]
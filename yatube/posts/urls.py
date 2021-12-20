# posts/urls.py
from django.urls import path

from .views import (GroupPostView, IndexView, PostCreate, PostDelete,
                    PostDetailView, PostEdit, ProfileDetailView)

app_name = 'posts'

urlpatterns = [
    path('', IndexView.as_view(), name='main'),
    path('group/<slug:slug>/', GroupPostView.as_view(), name='group_list'),
    path(
        'profile/<str:username>/',
        ProfileDetailView.as_view(),
        name='profile'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('posts/<int:post_id>/edit/', PostEdit.as_view(), name='post_edit'),
    path(
        'posts/<int:post_id>/delete/',
        PostDelete.as_view(),
        name='post_delete'),
]

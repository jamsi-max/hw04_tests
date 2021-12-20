from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from yatube.settings import COUNT_PAGINATOR_PAGE

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


class IndexView(ListView):
    model = Post
    template_name = 'posts/index.html'
    paginate_by = COUNT_PAGINATOR_PAGE


class GroupPostView(ListView):
    model = Post
    template_name = 'posts/group_list.html'
    paginate_by = COUNT_PAGINATOR_PAGE

    def get_queryset(self):
        return get_object_or_404(Group, slug=self.kwargs['slug']).posts.all()


class ProfileDetailView(ListView):
    model = Post
    paginate_by = COUNT_PAGINATOR_PAGE
    template_name = 'posts/profile.html'

    def get_queryset(self):
        return (
            Post.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .order_by('author'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts_count"] = Post.objects.filter(
            author=context["post"].author).count()
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context


class PostEdit(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'posts/create_post.html'

    def get_success_url(self):
        return reverse('posts:post_detail', args=[self.kwargs['post_id']])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        username = (
            get_object_or_404(Post, pk=self.kwargs['post_id'])
            .author.username)
        return reverse('posts:profile', args=[username])

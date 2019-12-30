from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy

from .models import UserProfile, Post, Tag, Category
from .forms import ProfileForm, PostForm

from django.contrib.auth.decorators import login_required   # 登录装饰器
from django.utils.decorators import method_decorator    # 函数装饰器转方法装饰器

from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger    # 分页


# 登录后主页
@login_required
def profile(request):
    user = request.user
    return render(request, 'account/profile.html', {'user': user})


# 登录后更新个人信息页
@login_required
def profile_update(request):
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            user_profile.org = form.cleaned_data['org']
            user_profile.telephone = form.cleaned_data['telephone']
            user_profile.save()

            return HttpResponseRedirect(reverse('blog:profile'))
    else:
        default_data = {'first_name': user.first_name, 'last_name': user.last_name,
                        'org': user_profile.org, 'telephone': user_profile.telephone}
        form = ProfileForm(default_data)

    return render(request, 'account/profile_update.html', {'form': form, 'user': user})


# 首页（不需要登录（登录后也是这个页面））：index.html
def index(request):
    user = request.user

    posts = Post.objects.all()
    paginator = Paginator(posts, 3, 2)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/index.html", {'user': user, 'posts': posts})


# 博客列表页：post_list.html
class PostListView(ListView):
    paginate_by = 10  # 每多少条博客分一页
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        return Post.objects.all().order_by('-published_time')


# 博客详情页（不需要登录（登录后也是这个页面））：post_detail.html
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.viewed()
        return obj

# 我的主页（需要登录）：myblog.html
@login_required()
def myblogView(request):
    post = Post.objects.filter(author=request.user)
    return render(request, 'blog/myblog.html', {'post': post})

# 草稿箱列表页（需要登录）：post_draft_list.html
@method_decorator(login_required, name='dispatch')
class PostDraftListView(ListView):
    template_name = 'blog/post_draft_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).filter(status='draft').order_by('-published_time')


# 已发表博客列表页（需要登录）：post_published_list.html
@method_decorator(login_required, name='dispatch')
class PostPublishedListView(ListView):
    template_name = 'blog/post_published_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-published_time')

# 添加博客页（需要登录）：post_create_form.html
@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    template_name = 'blog/post_create_form.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# 更新博客页（需要登录）：post_update_form.html
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_update_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404()

# 类别列表页（需要登录）：category_list.html
@method_decorator(login_required, name='dispatch')
class CategoryListView(ListView):
    template_name = 'blog/category_list.html'
    model = Category

# 类别详情页（需要登录）：category_detail.html
@method_decorator(login_required, name='dispatch')
class CategoryDetailView(DetailView):
    template_name = 'blog/category_detail.html'
    model = Category

# 标签列表页（需要登录）：tag_list.html
@method_decorator(login_required, name='dispatch')
class TagListView(ListView):
    template_name = 'blog/tag_list.html'
    model = Tag

# 标签详情页（需要登录）：tag_detail.html
@method_decorator(login_required, name='dispatch')
class TagDetailView(DetailView):
    template_name = 'blog/tag_detail.html'
    model = Tag

# 搜索页（不需要登录）：post_search.html
@login_required()
def post_search(request):
    return render(request, 'blog/post_search.html')

# 保存的草稿发布出去：
@login_required()
def post_publish(request, pk, slug):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.published()
    return redirect(reverse("blog:post_detail", args=[str(pk), slug]))

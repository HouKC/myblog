from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    # path('', views.index),
    re_path(r'^profile/$', views.profile, name='profile'),
    re_path(r'^profile/update/$', views.profile_update, name='profile_update'),

    # - 首页（不需要登录（登录后也是这个页面））：index.html
    path('', views.index, name='index'),

    # - 博客列表页：post_list.html
    path('post/list/', views.PostListView.as_view(), name='post_list'),

    # - 博客详情页（不需要登录（登录后也是这个页面））：post_detail.html
    re_path(r'^post/(?P<pk>\d+)/(?P<slug1>[-\w]+)/$', views.PostDetailView.as_view(), name='post_detail'),

    # 我的主页（需要登录）：myblog.html
    path('user/', views.myblogView, name='myblog'),

    # - 草稿箱列表页（需要登录）：post_draft_list.html
    path('draft/', views.PostDraftListView.as_view(), name='post_draft_list'),

    # - 已发表博客列表页（需要登录）：post_published_list.html
    path('admin/', views.PostPublishedListView.as_view(), name='published_post_list'),

    # - 添加博客页（需要登录）：post_create_form.html
    re_path(r'^post/create/$', views.PostCreateView.as_view(), name='post_create'),

    # - 更新博客页（需要登录）：post_update_form.html
    re_path(r'^post/(?P<pk>\d+)/(?P<slug>[-\w]+)/update/$', views.post_publish, name='post_publish'),

    # - 类别列表页（需要登录）：category_list.html
    re_path(r'^category/$', views.CategoryListView.as_view(), name='category_list'),

    # - 类别详情页（需要登录）：category_detail.html
    re_path(r'^category/(?P<slug>[-\w]+)/$', views.CategoryDetailView.as_view(), name='category_detail'),

    # - 标签列表页（需要登录）：tag_list.html
    re_path(r'^tags/$', views.TagListView.as_view(), name='tag_list'),

    # - 标签详情页（需要登录）：tag_detail.html
    re_path(r'^tags/(?P<slug>[-\w]+)/$', views.TagDetailView.as_view(), name='tag_detail'),

    # - 搜索页（不需要登录）：post_search.html
    re_path(r'^search/$', views.post_search, name='post_search'),
]

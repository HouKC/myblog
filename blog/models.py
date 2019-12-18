from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse


class User(models.Model):  # 用户表类
    name = models.CharField('用户名', max_length=20, null=False)  # 用户名
    password = models.CharField('密码', max_length=20, null=False)  # 密码
    email = models.EmailField('邮箱')     # 电子邮箱
    enabled = models.BooleanField(default=False)  # 是否登录，默认否

    def __str__(self):  # 设置输出User对象时的内容，也就是print(User对象)就会显示的内容
        return self.name


class Tag(models.Model):    # 标签表类
    name = models.CharField(max_length=80)  # 标签名
    created_time = models.DateTimeField(auto_now_add=True)  # 标签创建时间

    class Meta:
        ordering = ['created_time']     # 根据创建tag的时间排序

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):  # 博客表类
    choices = (
        ('draft', '草稿'),
        ('published', '发表'),
    )

    title = models.CharField('标题', max_length=200, unique=True)  # unique表示标题唯一
    slug = models.SlugField('简介', max_length=250)
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE,
                               related_name="author_posts")  # 外键关联User类，别名为"作者"，删除该对象时也删除与User的关联，related_name是支持反向搜索，允许通过作者搜索其所有文章
    body = models.TextField('正文')
    published_time = models.DateTimeField('发表时间', default=timezone.now, null=True)  # 发布时间可以为空，默认为当前时间
    created_time = models.DateTimeField('创建时间', auto_now_add=True)  # 创建时间自动生成，并且仅生成一次
    updated_time = models.DateTimeField('修改时间', auto_now=True)  # 更新时间自动追加
    status = models.CharField('文章状态', max_length=1, choices=choices,
                              default='published')  # 表示文章发表或者是草稿状态，默认发表，choices是替换了显示该字段时的字符
    tags = models.ManyToManyField('Tag', verbose_name='标签', blank=True)  # 标签是多对多
    views = models.PositiveIntegerField('浏览量', default=0)  # 浏览量为正整数，从0开始
    likenum = models.PositiveIntegerField('点赞', default=0)  # 点赞数

    objects = models.Manager()  # 默认的筛选器
    published = PublishedManager()  # 自定义筛选器，调用这个对象时会得到已经发表了的博客

    def __str__(self):
        return self.title

    def viewed(self):  # 浏览量自加1的函数
        self.views += 1
        self.save(update_fields=['views'])

    class Meta:
        ordering = ['-published_time']  # 按照发布时间从大到小排序
        verbose_name = "博客"  # 设置后台管理显示的字符
        verbose_name_plural = verbose_name  # 复数和单数显示的字符一致


class Comment(models.Model):    # 评论表类
    post = models.ForeignKey(Post, related_name='post_comments')     # 支持反向搜索，通过博客内容搜索该博客下的所有评论
    name = models.CharField(max_length=80)  # 评论用户的名称
    body = models.TextField()   # 评论内容
    created_time = models.DateTimeField(auto_now_add=True)   # 评论时间
    updated_time = models.DateTimeField(auto_now=True)  # 评论更新时间
    active = models.BooleanField(default=True)  # 评论激活状态，默认激活

    def __str__(self):  # 显示由谁对什么博客的评论
        return 'Comment by {} on {}'.format(self.name, self.post)

    class Meta:
        ordering = ['-created_time']

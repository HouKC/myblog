from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.urls import reverse
from unidecode import unidecode
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    org = models.CharField('组织', max_length=128, blank=True)
    telephone = models.CharField("电话", max_length=50, blank=True)
    last_mod_time = models.DateTimeField('最近更新时间', auto_now=True)

    def __str__(self):
        return "%s的个人信息" % self.user.__str__()

    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False

    class Meta:
        verbose_name = '用户个人信息'
        verbose_name_plural = verbose_name


class Category(models.Model):       # 分类表类
    name = models.CharField('分类名', max_length=80, unique=True)  # 类别名
    slug = models.SlugField('slug', max_length=60, blank=True)      # 保存slug，用于url
    parent_category = models.ForeignKey('self', verbose_name="父级分类", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):     # 创建该类时跳转到对应的详情页面中
        return reverse('blog:category_detail', args=[self.slug])

    def has_child(self):    # 判断是否存在子分类
        if self.category_set.all().count() > 0:
            return True
        return False

    class Meta:
        ordering = ['name']     # 根据创建category的名称排序
        verbose_name = "分类"
        verbose_name_plural = verbose_name


class Tag(models.Model):    # 标签表类
    name = models.CharField('标签名', max_length=80, unique=True)  # 标签名
    slug = models.SlugField('slug', max_length=60, blank=True)  # 保存slug，用于url

    def __str__(self):
        return self.name

    def get_absolute_url(self):     # 创建该类时跳转到对应的详情页面中
        return reverse('blog:tag_detail', args=[self.slug])

    def get_post_count(self):   # 查询包含该标签的博客（已发表）
        return Post.published.filter(tags__slug=self.slug).count()

    class Meta:
        ordering = ['name']     # 根据创建tag的名称排序
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):  # 博客表类
    choices = (
        ('draft', '草稿'),
        ('published', '发表'),
    )

    title = models.CharField('标题', max_length=200, unique=True)  # unique表示标题唯一
    slug = models.SlugField('slug', max_length=60, blank=True)  # 简短的标签，用于搜索引擎搜索时识别，主要用于url的设计中
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE,
                               related_name="author_posts")  # 外键关联User类，别名为"作者"，删除该对象时也删除与User的关联，related_name是支持反向搜索，允许通过作者搜索其所有文章
    body = models.TextField('正文')
    published_time = models.DateTimeField('发表时间', default=timezone.now, null=True)  # 发布时间可以为空，默认为当前时间
    created_time = models.DateTimeField('创建时间', auto_now_add=True)  # 创建时间自动生成，并且仅生成一次
    updated_time = models.DateTimeField('修改时间', auto_now=True)  # 更新时间自动追加
    status = models.CharField('文章状态', max_length=1, choices=choices,
                              default='published')  # 表示文章发表或者是草稿状态，默认发表，choices是替换了显示该字段时的字符
    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE, blank=False, null=False)  # 每篇博客只属于一类
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

    def like(self):     # 点赞数自加1的函数
        self.likenum += 1
        self.save(update_fields=['likenum'])

    def published(self):    # 博客发表函数
        self.status = 'published'
        self.published_time = timezone.now()
        self.save(update_fields=['status', 'published_time'])

    def save(self, *args, **kwargs):    # 保存时根据标题生成slug，以便放到url中，这样可以很容易从url看出是哪篇博客
        if not self.id or not self.slug:
            self.slug = slugify(unidecode(self.title))  # 根据标题生成slug
        super().save(*args, **kwargs)   # 调用父类save函数

    def clean(self):    # 草稿状态的博客没有发表时间，而发布状态的博客，发布日期为当前时间
        if self.status == 'draft' and self.published_time is not None:
            self.published_time = None
        if self.status == 'published' and self.published_time is None:
            self.published_time = timezone.now()

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[str(self.id), self.slug])  # 创建对象时自动跳转到详细编辑的页面

    class Meta:
        ordering = ['-published_time']  # 按照发布时间从大到小排序
        verbose_name = "博客"  # 设置后台管理显示的字符
        verbose_name_plural = verbose_name  # 复数和单数显示的字符一致


# class Comment(models.Model):    # 评论表类
#     post = models.ForeignKey(Post, related_name='post_comments')     # 支持反向搜索，通过博客内容搜索该博客下的所有评论
#     name = models.CharField(max_length=80)  # 评论用户的名称
#     body = models.TextField()   # 评论内容
#     created_time = models.DateTimeField(auto_now_add=True)   # 评论时间
#     updated_time = models.DateTimeField(auto_now=True)  # 评论更新时间
#     active = models.BooleanField(default=True)  # 评论激活状态，默认激活
#
#     def __str__(self):  # 显示由谁对什么博客的评论
#         return 'Comment by {} on {}'.format(self.name, self.post)
#
#     class Meta:
#         ordering = ['-created_time']

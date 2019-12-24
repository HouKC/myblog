from django import forms
from .models import UserProfile, Post


class ProfileForm(forms.Form):
    first_name = forms.CharField(label='姓氏', max_length=50, required=False)
    last_name = forms.CharField(label='名字', max_length=50, required=False)
    org = forms.CharField(label='组织', max_length=50, required=False)
    telephone = forms.CharField(label='电话', max_length=50, required=False)


class SignupForm(forms.Form):
    def signup(self, request, user):
        user_profile = UserProfile()
        user_profile.user = user
        user.save()
        user_profile.save()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author', 'views', 'slug', 'published_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'multi-checkbox'}),
        }
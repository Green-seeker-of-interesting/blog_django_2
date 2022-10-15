from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, label="Название")
    email = forms.EmailField(label="Ваша почта")
    to = forms.EmailField(label="Почта получателя")
    coments = forms.CharField(
        required=False, widget=forms.Textarea, label="Коментарий")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

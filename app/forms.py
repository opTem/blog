from django import forms


class CreatePublicationForm(forms.Form):
    name = forms.CharField()
    short_text = forms.CharField(widget=forms.Textarea())
    text = forms.CharField(widget=forms.Textarea())


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea())

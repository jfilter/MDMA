from django import forms
from .models import InputImage


class InputImageForm(forms.ModelForm):
    class Meta:
        model = InputImage
        fields = ('description', 'copyright_notice', 'image')

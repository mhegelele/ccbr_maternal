from django import forms


from .models import FormConfig


class FormConfigForm(forms.ModelForm):

    class Meta:
        model = FormConfig
        fields = ['name']

from .models import ManualCount
from django import forms




class ManualCountForm(forms.ModelForm):
    date = forms.CharField(widget=forms.TextInput(attrs={'type':'date'}))
    class Meta:
        model = ManualCount
        fields = '__all__'
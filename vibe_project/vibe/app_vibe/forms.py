from django import forms
from app_config.models import Cities, Schools


class MyForm(forms.Form):
    city = forms.ChoiceField(choices=[(city.id, city.title) for city in Cities.objects.all()])
    school = forms.ChoiceField(choices=[(school.id, f'{school.city.title} | {school.title}') for school in Schools.objects.all()])
    school_class = forms.IntegerField(min_value=5, max_value=11)
    names = forms.CharField(max_length=1000, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].label = 'Город: '
        self.fields['city'].widget.attrs.update({'id': 'id_username'})
        self.fields['school'].label = 'Школа: '
        self.fields['school'].widget.attrs.update({'id': 'id_username'})
        self.fields['school_class'].label = 'Класс: '
        self.fields['school_class'].widget.attrs.update({'id': 'id_username'})
        self.fields['names'].label = 'Имена: '
        self.fields['names'].widget.attrs.update({'id': 'id_username'})

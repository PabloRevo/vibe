from .models import Users
from .models import Cities, Schools
from django.shortcuts import render, redirect
from .forms import MyForm


def fake_view(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            city = int(form.cleaned_data.get('city'))
            city = Cities.objects.filter(id=city).get()
            school = int(form.cleaned_data.get('school'))
            school = Schools.objects.filter(id=school).get()
            school_class = int(form.cleaned_data.get('school_class'))
            names = form.cleaned_data.get('names')
            gender = 'Парень'
            for elem in names.split('\n'):
                if '\r' in elem:
                    name = elem.replace('\r', '')
                else:
                    name = elem
                Users(
                    user_id=1, city=city, school=school, school_class=school_class,
                    gender=gender, full_name=name, status_city=True, status_school=True
                ).save()
            return redirect('/admin/')
    else:
        form = MyForm()
    return render(request, 'fake.html', {'form': form})

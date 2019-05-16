import csv
import io

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from .models import PhonesList
import django_tables2 as tables
from django_tables2 import RequestConfig
from django.db.models import Q


class SimpleTable(tables.Table):
    class Meta:
        model = PhonesList
        exclude = ('custom_p_pk',)
        attrs = {'class': 'table table-striped table-bordered',
                 'thead': {
                     'class': 'thead-light'
                 }}


def phones_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        print(search_query)
        print(type)
        tables = SimpleTable(PhonesList.objects.filter(Q(org_name__icontains=search_query) |
                                                       Q(phone_number__icontains=search_query) |
                                                       Q(dep_head__icontains=search_query)))
        RequestConfig(request, paginate={'per_page': 10}).configure(tables)
    else:
        tables = SimpleTable(PhonesList.objects.all())
        RequestConfig(request, paginate={'per_page': 10}).configure(tables)
    return render(request, 'phonebook/index.html', {'tables': tables})


def phones_upload(request):
    if request.user.is_superuser:
        template = 'phonebook/phones_upload.html'
        if request.method == "GET":
            return render(request, template)
        csv_file = request.FILES['phone_file']
        data_set = csv_file.read().decode('Windows-1251')
        io_string = io.StringIO(data_set)
        next(io_string)
        data = {PhonesList.make_p_pk(column[0], column[1]): {
            'org_name': column[0],
            'phone_number': column[1],
            'dep_head': column[2],
        } for column in csv.reader(io_string, delimiter=';')}
        PhonesList.update_by_p_pk(data)
        return render(request, template)

from django.shortcuts import render
from .models import PhonesList
import django_tables2 as tables
from django_tables2 import RequestConfig


class SimpleTable(tables.Table):

    class Meta:
        model = PhonesList
        attrs = {'class': 'table table-striped table-bordered',
                 'thead': {
                     'class': 'thead-light'
                 },

                 }


def phones_list(request):
    tables = SimpleTable(PhonesList.objects.all())
    RequestConfig(request, paginate={'per_page': 15}).configure(tables)
    return render(request, 'phonebook/index.html', {'tables': tables})

import csv
import io

import django_tables2 as tables
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.shortcuts import render
from django_tables2 import RequestConfig

from .models import CallDetail
from phonebook.models import PhonesList


class CdlTable(tables.Table):
    class Meta:
        model = CallDetail
        exclude = ('custom_pk',)
        attrs = {
            'class': 'table table-striped table-bordered',
            'thead': {
                'class': 'thead-light'
            }
        }


@login_required(login_url='/accounts/login/')
@permission_required('asu.view_CallDetail')
def call_detail_list(request):
    search_query = request.GET.get('search', '')

    if search_query:
        cdl = CdlTable(CallDetail.objects.defer('custom_pk').filter(caller__icontains=search_query))
        RequestConfig(request, paginate={'per_page': 15}).configure(cdl)
    else:
        cdl = CdlTable(CallDetail.objects.defer('custom_pk').iterator())
        RequestConfig(request, paginate={'per_page': 15}).configure(cdl)
    return render(request, 'asu/CDL.html', {'cdl': cdl})


def detail_upload(request):
    template = 'asu/upload_csv.html'
    prompt = {
        'order': "Порядок в CSV файле должен быть Дата разговора;С телефона;На телефон;Код "
                 "города;Длительность;Сумма;Дата разговора (с секундами) "
    }
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    data_set = csv_file.read().decode('Windows-1251')
    io_string = io.StringIO(data_set)
    next(io_string)
    data = {CallDetail.make_pk(column[0], column[1]): {
        'talk_date': column[0],
        'caller': column[1],
        'ans_caller': column[2],
        'call_direction': column[3],
        'call_duration': column[4],
        'money': column[5],
    } for column in csv.reader(io_string, delimiter=';')}
    CallDetail.update_by_pk(data)
    return render(request, template)


def get_sum(request):
    template = 'asu/calc.html'

    if request.method == "GET":
        return render(request, template)

    d1 = request.POST.get('d1')
    d2 = request.POST.get('d2')
    summa = CallDetail.objects.filter(talk_date__gte=d1).filter(talk_date__lte=d2).aggregate(sum=Sum('money')).values()
    nsum = next(iter(summa))
    return render(request, template, {'summa': nsum, 'data_n': d1, 'data_p': d2})


def get_sum_otd(request):
    template = 'asu/asu.html'

    if request.method == "GET":
        o_name = PhonesList.objects.values_list('org_name', flat=True).distinct()

        return render(request, template, {'o_name': o_name})

    ch_org = request.POST.get('ch_name')
    d1 = request.POST.get('d1')
    d2 = request.POST.get('d2')

    ch_num = list(PhonesList.objects.filter(org_name__istartswith=ch_org).values_list('phone_number', flat=True))
    for num in ch_num:

        summa = CallDetail.objects.filter(
            talk_date__gte=d1).filter(
            talk_date__lte=d2).filter(caller__iexact=num).aggregate(sum=Sum('money')).values()
        o_sum = next(iter(summa))
        return render(request, template, {'o_sum': o_sum, 'ch_org': ch_org, 'data_n': d1, 'data_p': d2})

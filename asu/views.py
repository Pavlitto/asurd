import csv
import io

import django_tables2 as tables
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django_tables2 import RequestConfig

from .models import CallDetail


class CdlTable(tables.Table):
    class Meta:
        model = CallDetail
        attrs = {'class': 'table table-striped table-bordered',
                 'thead': {
                     'class': 'thead-light'
                 },

                 }


@login_required(login_url='/accounts/login/')
@permission_required('asu.view_CallDetail')
def call_detail_list(request):
    cdl = CdlTable(CallDetail.objects.all())
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
    for column in csv.reader(io_string, delimiter=';'):
        _, created = CallDetail.objects.update_or_create(
            talk_date=column[0],
            caller=column[1],
            ans_caller=column[2],
            call_direction=column[3],
            call_duration=column[4],
            money=column[5],
        )

    context = {}
    return render(request, template, context)

import csv
import io
from datetime import datetime, timedelta
from dateutil import relativedelta
from decimal import Decimal

import django_tables2 as tables
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig
from transliterate import translit

from phonebook.models import PhonesList
from .models import CallDetail


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


#   1 смотреть всю детализацию
@login_required(login_url='/accounts/login/')
@permission_required('asu.view_CallDetail')
def call_detail_list(request):
    search_query = request.GET.get('search', '')

    if search_query:
        cdl = CdlTable(CallDetail.objects.defer('custom_pk').filter(caller__icontains=search_query))
        RequestConfig(request, paginate={'per_page': 10}).configure(cdl)
    else:
        cdl = CdlTable(CallDetail.objects.defer('custom_pk').iterator())
        RequestConfig(request, paginate={'per_page': 10}).configure(cdl)
    return render(request, 'asu/CDL.html', {'cdl': cdl})


#   2 загружать детализацию
@login_required(login_url='/accounts/login/')
@permission_required('asu.get_sum', 'asu.view_CallDetail')
def detail_upload(request):
    template = 'asu/upload_csv.html'
    prompt = {
        'order': "Порядок в CSV файле должен быть Дата разговора;С телефона;На телефон;Код "
                 "города;Длительность;Сумма "
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
        'money': Decimal(column[5].replace(',', '.')),
    } for column in csv.reader(io_string, delimiter=';')}
    CallDetail.update_by_pk(data)
    return render(request, template)


#   3 получить общую сумму в браузере
@login_required(login_url='/accounts/login/')
@permission_required('asu.view_CallDetail')
def get_sum(request):
    template = 'asu/calc.html'

    if request.method == "GET":
        return render(request, template)

    d1 = request.POST.get('d1')
    data2_change = request.POST.get('d2')
    d2 = datetime.strptime(data2_change, "%Y-%m-%d") + timedelta(days=1)
    summa = CallDetail.objects.filter(talk_date__gte=d1).filter(talk_date__lte=d2).aggregate(sum=Sum('money')).values()
    nsum = next(iter(summa))

    return render(request, template, {'summa': round(nsum, 2), 'data1': d1, 'data2': data2_change})


#   4 получить сумму в бразуере по выбранным отделам
@login_required(login_url='/accounts/login/')
@permission_required('asu.view_CallDetail')
def get_sum_otd(request):
    template = 'asu/asu.html'

    if request.method == "GET":
        o_name = PhonesList.objects.values_list('org_name', flat=True).distinct()

        return render(request, template, {'o_name': o_name})

    ch_org = request.POST.get('ch_name')
    d1 = request.POST.get('d1')
    data2_change = request.POST.get('d2')
    d2 = datetime.strptime(data2_change, "%Y-%m-%d") + timedelta(days=1)

    ch_num = list(PhonesList.objects.filter(org_name__istartswith=ch_org).values_list('phone_number', flat=True))
    for num in ch_num:
        summa = CallDetail.objects.filter(
            talk_date__gte=d1).filter(
            talk_date__lte=d2).filter(
            caller__iexact=num).aggregate(
            sum=Sum('money')).values()
        o_sum = next(iter(summa))

        return render(request, template, {'o_sum': round(o_sum, 2), 'ch_org': ch_org})


#   5 скачать файл со всеми подразделениями
@login_required(login_url='/accounts/login/')
@permission_required('asu.get_sum', 'asu.view_CallDetail')
def download_sum_all_otd(request):
    d1 = request.POST.get('d1')
    data2_change = request.POST.get('d2')
    d2 = datetime.strptime(data2_change, "%Y-%m-%d") + timedelta(days=1)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="summa_po_vsem_za_period ' \
                                      + d1 + '_' + data2_change + '.csv" '

    writer = csv.writer(response, delimiter=';')
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow(['Наименование отдела', 'Номер телефона', 'Сумма разговоров за период'])
    phones = PhonesList.objects.values_list('phone_number', flat=True)
    for p in phones:
        summa = CallDetail.objects.filter(caller__exact=p).filter(talk_date__gte=d1).filter(
            talk_date__lte=d2).aggregate(sum=Sum('money'))
        round_sum = summa.get('sum')
        if type(round_sum) == Decimal:
            round_sum = str(round(round_sum, 2)).replace(".", ",")
        else:
            round_sum = ('аббонент не разговаривал')
        org = phones.filter(custom_p_pk__icontains=p).values_list('org_name', flat=True)
        writer.writerow([org[0], p, round_sum])
    return response


#   6 скачать файл конкретного отдела
@login_required(login_url='/accounts/login/')
@permission_required('asu.get_sum', 'asu.view_CallDetail')
def download_sum_otd(request):
    ch_org = request.POST.get('ch_name')
    d1 = request.POST.get('d1')
    data2_change = request.POST.get('d2')
    d2 = datetime.strptime(data2_change, "%Y-%m-%d") + timedelta(days=1)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= "' + d1 + '_' + data2_change + '.csv"'

    writer = csv.writer(response, delimiter=';')
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow(['Наименование отдела', 'Телефонный номер подразделения', 'Сумма разговоров за период'])
    items = PhonesList.objects.filter(custom_p_pk__icontains=ch_org).values_list('phone_number', flat=True)
    for i in items:
        summa = CallDetail.objects.filter(
            caller__iexact=i).filter(
            talk_date__gte=d1).filter(
            talk_date__lte=d2).aggregate(sum=Sum('money'))
        round_sum = summa.get('sum')
        if type(round_sum) == Decimal:
            round_sum = str(round(round_sum, 2)).replace(".", ",")
        else:
            round_sum = ('аббонент не разговаривал')
        writer.writerow([ch_org, i, round_sum])
    return response


#   7 выгрузка нарушений выбранного подразделения
@login_required(login_url='/accounts/login/')
@permission_required('asu.get_sum', 'asu.view_CallDetail')
def give_intruders(request):
    ch_org = request.POST.get('ch_name')
    tr_org = translit(ch_org, reversed=True)
    d1 = request.POST.get('d1')
    data2_change = request.POST.get('d2')
    d2 = datetime.strptime(data2_change, "%Y-%m-%d") + timedelta(days=1)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= "Narushenia ' + tr_org + ' c ' + d1 + ' po ' \
                                      + data2_change + '.csv"'

    writer = csv.writer(response, delimiter=';')
    response.write(u'\ufeff'.encode('utf8'))
    writer.writerow(['С какого номера произведен звонок', 'Куда звонили', 'Дата разговора', 'Длительность звонка'])
    phones = PhonesList.objects.filter(org_name__exact=ch_org).values_list('phone_number', flat=True)
    for p in phones:
        intruders = CallDetail.objects.filter(
            talk_date__gte=d1).filter(
            talk_date__lt=d2).filter(
            caller__exact=p).filter(
            call_duration__gt='5').values_list('caller', flat=True)
        cd = intruders.values_list('call_duration', flat=True)
        to_addr = intruders.values_list('ans_caller', flat=True)
        tdate = intruders.values_list('talk_date', flat=True)
        for i in range(intruders.count()):
            writer.writerow([intruders[i], to_addr[i], tdate[i], cd[i]])

    return response

#   8 визуализация сумм за последние пол года
@login_required(login_url='/accounts/login/')
@permission_required('asu.view_CallDetail')
def visualize_sum_month(request):
    template = 'asu/visual.html'
    summa = []
    datelabel = []
    ranger = 6
    now_date = datetime.now()
    fdate_dirty = now_date - relativedelta.relativedelta(months=ranger)
    fdate_o = fdate_dirty.strftime("%Y-%m")
    fdate_s = fdate_o + "-01 00:00:00"

    for m in range(0, ranger):
        datef = datetime.strptime(fdate_s, "%Y-%m-%d %H:%M:%S") + relativedelta.relativedelta(months=m)
        datel = datetime.strptime(fdate_s, "%Y-%m-%d %H:%M:%S") + relativedelta.relativedelta(months=m+1)
        sum = list(CallDetail.objects.filter(
            talk_date__gte=datef).filter(
            talk_date__lt=datel).aggregate(sum=Sum('money')).values())
        datelabel.append(datef.strftime("%m-%Y"))
        if sum[0] is None:
            sum[0] = int(0)
            summa.append(sum[0])
        else:
            sum[0] = float(round(sum[0], 2))
            summa.append(sum[0])
    return render(request, template, {'summa': summa, 'datelabel': datelabel})

from django.db import models


# Create your models here.
class CallDetail(models.Model):
    # Дата разговора
    talk_date = models.CharField(max_length=20, verbose_name='Дата разговора:')
    # С какого телефона
    caller = models.CharField(max_length=11, db_index=True, verbose_name='Звонили с телефона:')
    # Звонили на телефон
    ans_caller = models.CharField(max_length=12, db_index=True, verbose_name='Звонили на телефон:')
    # Код города
    call_direction = models.CharField(max_length=50, verbose_name='Направление:')
    # Длительность
    call_duration = models.IntegerField(verbose_name='Длительность звонка:')
    # Сумма
    money = models.CharField(max_length=11, verbose_name='Сумма:')
    # Дата разговора (с секундами)
    #talk_date_sec = models.DateTimeField(max_length=19, verbose_name='Дата разговора с секундами:')


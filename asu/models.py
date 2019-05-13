from django.db import models


class CallDetail(models.Model):
    custom_pk = models.CharField(primary_key=True, max_length=64)
    # Дата разговора
    talk_date = models.DateTimeField(verbose_name='Дата разговора:')
    # С какого телефона
    caller = models.CharField(max_length=11, verbose_name='Звонили с телефона:')
    # Звонили на телефон
    ans_caller = models.CharField(max_length=12, verbose_name='Звонили на телефон:')
    # Код города
    call_direction = models.CharField(max_length=50, verbose_name='Направление:')
    # Длительность
    call_duration = models.IntegerField(verbose_name='Длительность звонка:')
    # Сумма
    money = models.CharField(max_length=11, verbose_name='Сумма:')

    # money = models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Сумма:')
    # Дата разговора (с секундами)
    # talk_date_sec = models.DateTimeField(max_length=19, verbose_name='Дата разговора с секундами:')

    class Meta:
        unique_together = ('talk_date', 'caller')
        permissions = [('view_CallDetail', 'Can view /detail/ url')]

    def __str__(self):
        return self.custom_pk

    @staticmethod
    def make_pk(talk_date: str, caller: str):
        return talk_date + caller

    @classmethod
    def pk_exists(cls, pks: list):
        """ :pks - list of primary keys """
        size = 256
        res = set()
        for i in range(0, len(pks), size):
            res |= set(cls.objects.filter(custom_pk__in=pks[i:i + size]).values_list('custom_pk', flat=True))
        return res

    @classmethod
    def update_by_pk(cls, data: dict):
        """ :data - like {pk: {fields}} """
        exists = cls.pk_exists(list(data.keys()))

        cls.objects.bulk_create(
            cls(custom_pk=k, **v) for k, v in data.items() if k not in exists
        )

    def save(self, **kwargs):
        self.custom_pk = self.make_pk(self.talk_date.strftime('%Y-%m-%d %H:%M:%S'), self.caller)
        super().save(**kwargs)

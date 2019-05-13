from django.db import models


# Create your models here.
class PhonesList(models.Model):
    # отдел
    custom_p_pk = models.CharField(primary_key=True, max_length=64)
    org_name = models.CharField(max_length=50, db_index=True, verbose_name='Подразделение:')
    # номер телефона
    phone_number = models.CharField(max_length=10, verbose_name='Номер телефона:')
    # ответственный сотрудник
    dep_head = models.CharField(max_length=30, blank=True, verbose_name='Ответственный за телефонный номер:')

    class Meta:
        unique_together = ('org_name', 'phone_number')

    def __str__(self):
        return self.custom_p_pk

    @staticmethod
    def make_p_pk(org_name: str, phone_number: str):
        return org_name + phone_number

    @classmethod
    def pk_exists(cls, pks: list):
        """ :pks - list of primary keys """
        size = 20
        res = set()
        for i in range(0, len(pks), size):
            res |= set(cls.objects.filter(custom_p_pk__in=pks[i:i + size]).values_list('custom_p_pk', flat=True))
        return res

    @classmethod
    def update_by_p_pk(cls, data: dict):
        """ :data - like {pk: {fields}} """
        exists = cls.pk_exists(list(data.keys()))

        cls.objects.bulk_create(
            cls(custom_p_pk=k, **v) for k, v in data.items() if k not in exists
        )

    def save(self, **kwargs):
        self.custom_p_pk = self.make_p_pk(self.org_name, self.phone_number)
        super().save(**kwargs)

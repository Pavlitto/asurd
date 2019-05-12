from django.db import models


# Create your models here.
class PhonesList(models.Model):
    # отдел
    org_name = models.CharField(max_length=50, db_index=True, verbose_name='Отдел:')
    # номер телефона
    phone_number = models.CharField(max_length=11, unique=True, blank=True, verbose_name='Номер телефона:')
    # ответственный сотрудник
    dep_head = models.CharField(max_length=30, blank=True, verbose_name='Ответственный за телефонный номер:')

    def __str__(self):
        """A string representation of the model."""
        return self.org_name

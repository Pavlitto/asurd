# Generated by Django 2.2.1 on 2019-05-15 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PhonesList',
            fields=[
                ('custom_p_pk', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('org_name', models.CharField(db_index=True, max_length=50, verbose_name='Подразделение:')),
                ('phone_number', models.CharField(max_length=10, verbose_name='Номер телефона:')),
                ('dep_head', models.CharField(blank=True, max_length=30, verbose_name='Ответственный за телефонный номер:')),
            ],
            options={
                'unique_together': {('org_name', 'phone_number')},
            },
        ),
    ]

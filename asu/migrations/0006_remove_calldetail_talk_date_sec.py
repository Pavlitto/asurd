# Generated by Django 2.2.1 on 2019-05-12 08:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asu', '0005_auto_20190512_0804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calldetail',
            name='talk_date_sec',
        ),
    ]

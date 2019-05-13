from django.contrib import admin
from phonebook.models import PhonesList


@admin.register(PhonesList)
class PhonesListAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'phone_number', 'dep_head')
    list_filter = ('org_name', )
    exclude = ('custom_pk', )

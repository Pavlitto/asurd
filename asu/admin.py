from django.contrib import admin
from asu.models import CallDetail


@admin.register(CallDetail)
class CallDetailAdmin(admin.ModelAdmin):
    list_display = ('talk_date', 'caller', 'ans_caller', 'call_direction', 'call_duration', 'money')
    list_filter = ('call_direction', )
    date_hierarchy = 'talk_date'
    exclude = ('custom_pk', )

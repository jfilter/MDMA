from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import STATUS_WATING, InputImage, Job, StyleImage, User

admin.site.register(User, UserAdmin)
admin.site.register(StyleImage)
admin.site.register(InputImage)


def reset_status(modeladmin, request, queryset):
    queryset.update(status=STATUS_WATING, job_started_at=None,
                    job_finished_at=None, output_image=None)


reset_status.short_description = "reset status"


class JobAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'status',
                    'job_started_at', 'job_finished_at']
    ordering = ['-created_at']
    actions = [reset_status]


admin.site.register(Job, JobAdmin)

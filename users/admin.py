from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            'SoftDesk',
            {
                'fields': (
                    'age',
                    'can_be_contacted',
                    'can_data_be_shared',
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'SoftDesk',
            {
                'fields': (
                    'age',
                    'can_be_contacted',
                    'can_data_be_shared',
                )
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)

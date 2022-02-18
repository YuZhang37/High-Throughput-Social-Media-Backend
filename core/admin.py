from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # add_fieldsets: the fields we see when register a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2',
                       'email', 'first_name', 'last_name'),
        }),
        # email is required because we set it to be unique
        # username and password1 and password2 are required because of the
        # User Model default implementation
    )
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ('first_name', 'last_name')

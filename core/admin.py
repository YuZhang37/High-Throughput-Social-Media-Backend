from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, UserProfile


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

# the following implementation
# is also compatible for codes using the django user model


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'nickname', 'avatar', 'user', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user_profiles'
    fields = ['nickname', 'avatar', 'user']


class UserAdmin2(DjangoUserAdmin):
    list_display = (
        'id', 'username', 'email', 'is_staff', 'date_joined',
        'first_name', 'last_name',
    )
    # for the adding page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2',
                       'email', 'first_name', 'last_name'),
        }),
    )
    date_hierarchy = 'date_joined'
    inlines = (UserProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin2)

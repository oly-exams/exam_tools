from django.contrib import admin

# User should not be imported directly (pylint-django:E5142)
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


from ipho_core.models import (
    AccountRequest,
    Delegation,
    PushSubscription,
    RandomDrawLog,
    Student,
)

# Register your models here.


@admin.action(description="Activate selected accounts")
def activate_users(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.update(is_active=True)


@admin.action(description="De-activate selected accounts")
def deactivate_users(modeladmin, request, queryset):  # pylint: disable=unused-argument
    queryset.filter(is_superuser=False).update(is_active=False)


class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ("is_active", "last_login")
    actions = [activate_users, deactivate_users]


class DelegationAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    filter_horizontal = ("members",)


class StudentAdmin(admin.ModelAdmin):
    fields = (
        "code",
        ("first_name", "last_name"),
        "delegation",
    )
    list_display = (
        "code",
        "last_name",
        "first_name",
        "delegation",
    )
    search_fields = ("last_name", "first_name")
    list_editable = ("first_name", "last_name", "delegation")
    list_filter = ("delegation",)


class AccountRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "timestamp")
    search_fields = ("user", "email")
    list_filter = ("user",)


class PushSubscriptionAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Delegation, DelegationAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(AccountRequest, AccountRequestAdmin)
admin.site.register(PushSubscription, PushSubscriptionAdmin)
admin.site.register(RandomDrawLog)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from users.models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Админка для кастомной модели пользователя."""

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
        "avatar_preview",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("avatar",)}),
    )

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "-"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок."""

    list_display = ("id", "user", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "user__username",
        "user__email",
        "author__username",
        "author__email",
    )
    autocomplete_fields = ("user", "author")
    list_select_related = ("user", "author")
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "author")

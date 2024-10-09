# admin.py
from django.contrib import admin
from .models import User
from django.utils.html import format_html
from django.utils.translation import gettext as _

# # Inline for friends
# class FriendsInline(admin.TabularInline):
#     model = User.friends.through  # The intermediary table for the ManyToMany relationship
#     fk_name = 'from_user'  # Specify the ForeignKey field from the intermediary model to the User model
#     extra = 1  # Number of empty forms for adding friends

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'avatar_tag', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

    # Add inlines to show the friends in the admin
    # inlines = (FriendsInline,)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('avatar',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    search_fields = ('username',)
    ordering = ('username',)

    def avatar_tag(self, obj):
        default_avatar_url = 'https://api.dicebear.com/9.x/notionists/svg?seed=Jack'  # Replace with the actual path to your default avatar image
        avatar_url = obj.avatar.url if obj.avatar else default_avatar_url
        return format_html('<img src="{}" style="height: 50px; width: 50px; border-radius: 50%;" />', avatar_url)
    avatar_tag.short_description = _('Avatar')

# Register the updated UserAdmin
admin.site.register(User, UserAdmin)

# admin.py
from django.contrib import admin
from .models import User

# Inline for friends
class FriendsInline(admin.TabularInline):
    model = User.friends.through  # The intermediary table for the ManyToMany relationship
    fk_name = 'from_user'  # Specify the ForeignKey field from the intermediary model to the User model
    extra = 1  # Number of empty forms for adding friends

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

    # Add inlines to show the friends in the admin
    inlines = (FriendsInline,)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('city', 'country')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Game', {'fields': ('played_games', 'wins', 'defeats')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    search_fields = ('username', 'city', 'country')
    ordering = ('username',)

# Register the updated UserAdmin
admin.site.register(User, UserAdmin)

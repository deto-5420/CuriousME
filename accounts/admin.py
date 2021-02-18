from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User, Profile, Websites, UserFollowing,ProfessionList
from import_export.admin import ImportExportModelAdmin


admin.site.unregister(Group)

# User model admin Configuration
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    # The forms to add and change user instances

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id','email', 'username', 'is_admin', 'status', 'is_moderator')
    list_filter = ('is_admin', 'status', 'is_moderator')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'status')}),
        ('Permissions', {'fields': ('is_admin','is_active','is_staff','is_moderator')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
        ),
    )
    
    search_fields = ('email', 'username',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)

# @admin.register(User)
# class UserImportExportAdmin(ImportExportModelAdmin):
#     pass


# User Profile model admin Configuration
@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id','fullname','user')
    ordering = ('id','fullname',)
    search_fields = ('fullname',)
    

# Admin panel branding
admin.site.site_header = 'Collectanea'
admin.site.site_title = 'Collectanea Admin Portal'
admin.site.index_title = 'Welome to Collectanea SuperAdministration'


# class WebsiteAdmin(admin.ModelAdmin):
#     exclude = ['user_id']


@admin.register(Websites)
class WebsiteAdmin(ImportExportModelAdmin):
    pass

@admin.register(UserFollowing)
class WebsiteAdmin(ImportExportModelAdmin):
    pass

@admin.register(ProfessionList)
class WebsiteAdmin(ImportExportModelAdmin):
    pass

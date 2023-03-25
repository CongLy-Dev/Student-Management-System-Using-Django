from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Department)
admin.site.register(Major)
admin.site.register(Grade)
admin.site.register(Subject)
admin.site.register(Session)
admin.site.register(Assign)
# admin.site.register(AssignTime)
admin.site.register(Csv)

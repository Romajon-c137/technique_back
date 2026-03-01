from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    """Форма для создания нового пользователя в админ-панели"""
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('phone', 'full_name', 'role', 'is_active')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Форма для редактирования пользователя в админ-панели"""
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        help_text='Пароли хранятся в зашифрованном виде. '
                  '<a href="../password/">Изменить пароль</a>.'
    )
    
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для управления пользователями"""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('phone', 'full_name', 'role', 'is_active', 'created_at', 'last_login_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('phone', 'full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Личная информация', {'fields': ('full_name', 'avatar', 'birth_date')}),
        ('Права доступа', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login_at', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'role', 'password1', 'password2', 'is_active'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login_at')
    
    filter_horizontal = ()

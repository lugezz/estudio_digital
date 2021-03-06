import re
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from common.models import (Address, User, Document, Comment, APISettings,
                            Empresa, Impuesto)

class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ('street', 'address_line', 'city',
                  'state', 'postcode', 'country')

    def __init__(self, *args, **kwargs):
        account_view = kwargs.pop('account', False)

        super(AddressForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        self.fields['street'].widget.attrs.update({
            'placeholder': 'Calle'})
        self.fields['address_line'].widget.attrs.update({
            'placeholder': 'Número'})
        self.fields['city'].widget.attrs.update({
            'placeholder': 'Ciudad'})
        self.fields['state'].widget.attrs.update({
            'placeholder': 'Provincia'})
        self.fields['postcode'].widget.attrs.update({
            'placeholder': 'Código Postal'})
        self.fields["country"].choices = [
            ("", "--País--"), ] + list(self.fields["country"].choices)[1:]

        if account_view:
            self.fields['address_line'].required = True
            self.fields['street'].required = True
            self.fields['city'].required = True
            self.fields['state'].required = True
            self.fields['postcode'].required = True
            self.fields['country'].required = True


class UserForm(forms.ModelForm):

    password = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name',
                  'username', 'role', 'profile_pic']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        if not self.instance.pk:
            self.fields['password'].required = True

        # self.fields['password'].required = True

    # def __init__(self, args: object, kwargs: object) -> object:
    #     super(UserForm, self).__init__(*args, **kwargs)
    #
    #     self.fields['first_name'].required = True
    #     self.fields['username'].required = True
    #     self.fields['email'].required = True
    #
        # if not self.instance.pk:
        #     self.fields['password'].required = True

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 4:
                raise forms.ValidationError(
                    'La contraseña debe tener al menos 4 caracteres!')
        return password

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self.instance.id:
            if self.instance.email != email:
                if not User.objects.filter(
                        email=self.cleaned_data.get("email")).exists():
                    return self.cleaned_data.get("email")
                raise forms.ValidationError('Email already exists')
            else:
                return self.cleaned_data.get("email")
        else:
            if not User.objects.filter(
                    email=self.cleaned_data.get("email")).exists():
                return self.cleaned_data.get("email")
            raise forms.ValidationError('User already exists with this email')

class EmpresaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        asignado_impuestos = kwargs.pop('asignado_a', [])
        super(EmpresaForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        self.fields['descripcion'].widget.attrs.update({
            'rows': '6'})
        self.fields['asignado_a'].queryset = asignado_impuestos
        self.fields['asignado_a'].required = False


        for key, value in self.fields.items():
            if key == 'telefono':
                value.widget.attrs['placeholder'] = "+54-351-456-7890"
            elif key == 'descripcion':
                value.widget.attrs['placeholder'] = "Descripción"
            else:
                value.widget.attrs['placeholder'] = value.label

    class Meta:
        model = Empresa
        fields = ['nombre', 'CUIT', 'DGR', 'mail', 'telefono', 'direccion', 'descripcion', 'asignado_a']

class ImpuestoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImpuestoForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}
        self.fields['descripcion'].widget.attrs.update({
            'rows': '6'})

        for key, value in self.fields.items():
            if key == 'descripcion':
                value.widget.attrs['placeholder'] = "Descripción"
            else:
                value.widget.attrs['placeholder'] = value.label

    class Meta:
        model = Impuesto
        fields = ['nombre', 'tipo', 'periodicidad', 'div_venc', 'pri_dia', 'descripcion']


class LoginForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 4:
                raise forms.ValidationError(
                    'La contraseña debe tener al menos 4 caracteres!')
        return password

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user:
                if not self.user.is_active:
                    pass
                    # raise forms.ValidationError("User is Inactive")
            else:
                pass
                # raise forms.ValidationError("Invalid email and password")
        return self.cleaned_data


class ChangePasswordForm(forms.Form):
    CurrentPassword = forms.CharField(max_length=100)
    Newpassword = forms.CharField(max_length=100)
    confirm = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_confirm(self):
        if len(self.data.get('confirm')) < 4:
            raise forms.ValidationError(
                'La contraseña debe tener al menos 4 caracteres!')
        if self.data.get('confirm') != self.cleaned_data.get('Newpassword'):
            raise forms.ValidationError(
                'Confirme que la contraseña sea diferente')
        return self.data.get('confirm')


class PasswordResetEmailForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email,
                                   is_active=True).exists():
            raise forms.ValidationError("No hay un usuario con este email")
        return email


class DocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        users = kwargs.pop('users', [])
        super(DocumentForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

        self.fields['status'].choices = [
            (each[0], each[1]) for each in Document.DOCUMENT_STATUS_CHOICE]
        self.fields['status'].required = False
        self.fields['title'].required = True
        self.fields['shared_to'].queryset = users
        self.fields['shared_to'].required = False

    class Meta:
        model = Document
        fields = ['title', 'document_file', 'status', 'shared_to']


class UserCommentForm(forms.ModelForm):
    comment = forms.CharField(max_length=64, required=True)

    class Meta:
        model = Comment
        fields = ('comment', 'user', 'commented_by')


def find_urls(string):
    # website_regex = "^((http|https)://)?([A-Za-z0-9.-]+\.[A-Za-z]{2,63})?$"  # (http(s)://)google.com or google.com
    # website_regex = "^https?://([A-Za-z0-9.-]+\.[A-Za-z]{2,63})?$"  # (http(s)://)google.com
    # http(s)://google.com
    website_regex = "^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$"
    # http(s)://google.com:8000
    website_regex_port = "^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,63}:[0-9]{2,4}$"
    url = re.findall(website_regex, string)
    url_port = re.findall(website_regex_port, string)
    if url and url[0] != '':
        return url
    return url_port


class APISettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(APISettingsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs = {"class": "form-control"}

        # self.fields['title'].widget.attrs.update({
        #     'placeholder': 'Project Name'})
        # self.fields['lead_assigned_to'].widget.attrs.update({
        #     'placeholder': 'Assign Leads To'})

    class Meta:
        model = APISettings
        fields = ('title', 'website')

    def clean_website(self):
        website = self.data.get('website')
        if website and not (website.startswith('http://') or
                            website.startswith('https://')):
            raise forms.ValidationError("Please provide valid schema")
        if not len(find_urls(website)) > 0:
            raise forms.ValidationError(
                "Please provide a valid URL with schema and without trailing \
                slash - Example: http://google.com")
        return website

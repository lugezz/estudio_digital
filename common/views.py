import os
import json
import requests
import datetime
from django.contrib.auth import logout, authenticate, login
from django.db.models import Q
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import (HttpResponseRedirect,
                         JsonResponse, HttpResponse,
                         Http404)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View, DeleteView)
from common.models import (User, Document, Attachments,
                           Comment, APISettings,
                           Empresa, Impuesto)
from common.forms import (
    UserForm, LoginForm,
    ChangePasswordForm, PasswordResetEmailForm,
    DocumentForm, UserCommentForm,
    APISettingsForm, EmpresaForm, ImpuestoForm
)
from common.utils import COUNTRIES
from common.forms import AddressForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy, reverse
from django.conf import settings
from contacts.models import Contact
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
import boto3
import botocore


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


class AdminRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.raise_exception = True
        if not request.user.role == "ADMIN":
            if not request.user.is_superuser:
                return self.handle_no_permission()
        return super(AdminRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "sales/index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        contacts = Contact.objects.all()
        if self.request.user.role == "ADMIN" or self.request.user.is_superuser:
            pass
        else:
            contacts = contacts.filter(
                Q(created_by=self.request.user.id))

        context["contacts_count"] = contacts.count()
        return context


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = "change_password.html"

    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        context["change_password_form"] = ChangePasswordForm()
        return context

    def post(self, request, *args, **kwargs):
        error, errors = "", ""
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if not check_password(request.POST.get('CurrentPassword'),
                                  user.password):
                error = "Invalid old password"
            else:
                user.set_password(request.POST.get('Newpassword'))
                user.is_active = True
                user.save()
                return HttpResponseRedirect('/')
        else:
            errors = form.errors
        return render(request, "change_password.html",
                      {'error': error, 'errors': errors,
                       'change_password_form': form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):

        context = super(ProfileView, self).get_context_data(**kwargs)
        context["user_obj"] = self.request.user
        return context


class LoginView(TemplateView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context["GP_CLIENT_SECRET"] = settings.GP_CLIENT_SECRET
        context["GP_CLIENT_ID"] = settings.GP_CLIENT_ID
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST, request=request)
        if form.is_valid():

            user = User.objects.filter(email=request.POST.get('email')).first()
            # user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
            if user is not None:
                if user.is_active:
                    user = authenticate(username=request.POST.get(
                        'email'), password=request.POST.get('password'))

                    if user is not None:
                        login(request, user)
                        return HttpResponseRedirect('/')
                    return render(request, "login.html", {
                        "GP_CLIENT_SECRET": settings.GP_CLIENT_SECRET,
                        "GP_CLIENT_ID": settings.GP_CLIENT_ID,
                        "error": True,
                        "message":
                        "Your username and password didn't match. \
                        Please try again."
                    })
                return render(request, "login.html", {
                    "GP_CLIENT_SECRET": settings.GP_CLIENT_SECRET,
                    "GP_CLIENT_ID": settings.GP_CLIENT_ID,
                    "error": True,
                    "message":
                    "Your Account is inactive. Please Contact Administrator"
                })
            return render(request, "login.html", {
                "GP_CLIENT_SECRET": settings.GP_CLIENT_SECRET,
                "GP_CLIENT_ID": settings.GP_CLIENT_ID,
                "error": True,
                "message":
                "Your Account is not Found. Please Contact Administrator"
            })

        return render(request, "login.html", {
            "GP_CLIENT_SECRET": settings.GP_CLIENT_SECRET,
            "GP_CLIENT_ID": settings.GP_CLIENT_ID,
            # "error": True,
            # "message": "Your username and password didn't match. Please try again."
            "form": form
        })


class ForgotPasswordView(TemplateView):
    template_name = "forgot_password.html"


class LogoutView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.flush()
        return redirect("common:login")


class UsersListView(AdminRequiredMixin, TemplateView):
    model = User
    context_object_name = "users"
    template_name = "list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)
        context["users"] = self.get_queryset()
        context["per_page"] = self.request.POST.get('per_page')
        context['admin_email'] = settings.ADMIN_EMAIL
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CreateUserView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "create.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        if form.cleaned_data.get("password"):
            user.set_password(form.cleaned_data.get("password"))
        user.save()

        mail_subject = 'Cuenta creada en Estudio Digital'
        message = render_to_string('new_user.html', {
            'user': user,
            'created_by': self.request.user

        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.content_subtype = "html"
        email.send()

        if self.request.is_ajax():
            data = {'success_url': reverse_lazy(
                'common:users_list'), 'error': False}
            return JsonResponse(data)
        return super(CreateUserView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(CreateUserView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return response

    def get_context_data(self, **kwargs):
        context = super(CreateUserView, self).get_context_data(**kwargs)
        context["user_form"] = context["form"]
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return context


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    context_object_name = "users"
    template_name = "user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        address_form = AddressForm(request.POST)
        user_obj = self.object
        users_data = []
        context.update({
            "user_obj": user_obj,
            "contacts": Contact.objects.filter(),
            "comments": user_obj.user_comments.all(),
        })
        return context


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "create.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        if self.request.is_ajax():
            if (self.request.user.role != "ADMIN" and not
                    self.request.user.is_superuser):
                if self.request.user.id != self.object.id:
                    data = {'error_403': True, 'error': True}
                    return JsonResponse(data)
        if user.role == "USER":
            user.is_superuser = False
        user.save()
        if (self.request.user.role == "ADMIN" and
                self.request.user.is_superuser):
            if self.request.is_ajax():
                data = {'success_url': reverse_lazy(
                    'common:users_list'), 'error': False}
                return JsonResponse(data)
        if self.request.is_ajax():
            data = {'success_url': reverse_lazy(
                'common:profile'), 'error': False}
            return JsonResponse(data)
        return super(UpdateUserView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(UpdateUserView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return response

    def get_context_data(self, **kwargs):
        context = super(UpdateUserView, self).get_context_data(**kwargs)
        context["user_obj"] = self.object
        user_profile_name = str(context["user_obj"].profile_pic).split("/")
        user_profile_name = user_profile_name[-1]
        context["user_profile_name"] = user_profile_name
        context["user_form"] = context["form"]
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return context

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("common:users_list")

class PasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    form_class = PasswordResetEmailForm
    email_template_name = 'registration/password_reset_email.html'

def document_create(request):
    template_name = "doc_create.html"

    users = User.objects.filter(is_active=True).order_by('email')
    form = DocumentForm(users=users)
    if request.POST:
        form = DocumentForm(request.POST, request.FILES, users=users)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.created_by = request.user
            doc.save()
            if request.POST.getlist('shared_to'):
                doc.shared_to.add(*request.POST.getlist('shared_to'))
            data = {'success_url': reverse_lazy(
                'common:doc_list'), 'error': False}
            return JsonResponse(data)
        return JsonResponse({'error': True, 'errors': form.errors})
    context = {}
    context["doc_form"] = form
    context["users"] = users
    context["errors"] = form.errors
    return render(request, template_name, context)


class DocumentListView(LoginRequiredMixin, TemplateView):
    model = Document
    context_object_name = "documents"
    template_name = "doc_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        if self.request.user.is_superuser or self.request.user.role == "ADMIN":
            queryset = queryset
        else:
            if self.request.user.documents():
                doc_ids = self.request.user.documents().values_list('id',
                                                                    flat=True)
                shared_ids = queryset.filter(
                    Q(status='active') &
                    Q(shared_to__id__in=[self.request.user.id])).values_list(
                    'id', flat=True)
                queryset = queryset.filter(
                    Q(id__in=doc_ids) | Q(id__in=shared_ids))
            else:
                queryset = queryset.filter(Q(status='active') & Q(
                    shared_to__id__in=[self.request.user.id]))

        request_post = self.request.POST
        if request_post:
            if request_post.get('doc_name'):
                queryset = queryset.filter(
                    title__icontains=request_post.get('doc_name'))
            if request_post.get('status'):
                queryset = queryset.filter(status=request_post.get('status'))

            if request_post.getlist('shared_to'):
                queryset = queryset.filter(
                    shared_to__id__in=request_post.getlist('shared_to'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DocumentListView, self).get_context_data(**kwargs)
        context["users"] = User.objects.filter(
            is_active=True).order_by('email')
        context["documents"] = self.get_queryset()
        context["status_choices"] = Document.DOCUMENT_STATUS_CHOICE
        context["sharedto_list"] = [
            int(i) for i in self.request.POST.getlist('shared_to', []) if i]
        context["per_page"] = self.request.POST.get('per_page')

        search = False
        if (
            self.request.POST.get('doc_name') or
            self.request.POST.get('status') or
            self.request.POST.get('shared_to')
        ):
            search = True

        context["search"] = search
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document

    def get(self, request, *args, **kwargs):
        if not request.user.role == 'ADMIN':
            if not request.user == Document.objects.get(id=kwargs['pk']).created_by:
                raise PermissionDenied
        self.object = self.get_object()
        self.object.delete()
        return redirect("common:doc_list")


def document_update(request, pk):
    template_name = "doc_create.html"
    users = User.objects.filter(is_active=True).order_by('email')
    form = DocumentForm(users=users)
    document = Document.objects.filter(id=pk).first()

    if request.POST:
        form = DocumentForm(request.POST, request.FILES,
                            instance=document, users=users)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.save()

            doc.shared_to.clear()
            if request.POST.getlist('shared_to'):
                doc.shared_to.add(*request.POST.getlist('shared_to'))

            data = {'success_url': reverse_lazy(
                'common:doc_list'), 'error': False}
            return JsonResponse(data)
        return JsonResponse({'error': True, 'errors': form.errors})
    context = {}
    context["doc_obj"] = document
    context["doc_form"] = form
    context["doc_file_name"] = context["doc_obj"].document_file.name.split(
        "/")[-1]
    context["users"] = users
    context["sharedto_list"] = [
        int(i) for i in request.POST.getlist('shared_to', []) if i]
    context["errors"] = form.errors
    return render(request, template_name, context)


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = "doc_detail.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.role == 'ADMIN':
            if (not request.user ==
                    Document.objects.get(id=kwargs['pk']).created_by):
                raise PermissionDenied

        return super(DocumentDetailView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentDetailView, self).get_context_data(**kwargs)
        # documents = Document.objects.all()
        context.update({
            "file_type_code": self.object.file_type()[1],
            "doc_obj": self.object,
        })
        return context


def download_document(request, pk):
    doc_obj = Document.objects.filter(id=pk).last()
    if doc_obj:
        if not request.user.role == 'ADMIN':
            if (not request.user == doc_obj.created_by and
                    request.user not in doc_obj.shared_to.all()):
                raise PermissionDenied
        if settings.STORAGE_TYPE == "normal":
            # print('no no no no')
            path = doc_obj.document_file.path
            file_path = os.path.join(settings.MEDIA_ROOT, path)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + \
                        os.path.basename(file_path)
                    return response
        else:
            file_path = doc_obj.document_file
            file_name = doc_obj.title
            # print(file_path)
            # print(file_name)
            BUCKET_NAME = "django-crm-demo"
            KEY = str(file_path)
            s3 = boto3.resource('s3')
            try:
                s3.Bucket(BUCKET_NAME).download_file(KEY, file_name)
                # print('got it')
                with open(file_name, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + \
                        os.path.basename(file_name)
                os.remove(file_name)
                return response
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise

            return path
    raise Http404


def download_attachment(request, pk):
    attachment_obj = Attachments.objects.filter(id=pk).last()
    if attachment_obj:
        if settings.STORAGE_TYPE == "normal":
            path = attachment_obj.attachment.path
            file_path = os.path.join(settings.MEDIA_ROOT, path)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + \
                        os.path.basename(file_path)
                    return response
        else:
            file_path = attachment_obj.attachment
            file_name = attachment_obj.file_name
            # print(file_path)
            # print(file_name)
            BUCKET_NAME = "django-crm-demo"
            KEY = str(file_path)
            s3 = boto3.resource('s3')
            try:
                s3.Bucket(BUCKET_NAME).download_file(KEY, file_name)
                with open(file_name, 'rb') as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/vnd.ms-excel")
                    response['Content-Disposition'] = 'inline; filename=' + \
                        os.path.basename(file_name)
                os.remove(file_name)
                return response
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise
            # if file_path:
            #     print('yes tus pus')
    raise Http404


def change_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return HttpResponseRedirect('/users/list/')

def change_empresa_status(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if empresa.is_active:
        empresa.is_active = False
    else:
        empresa.is_active = True
    empresa.save()
    return HttpResponseRedirect('/empresas/list/')

def add_comment(request):
    if request.method == "POST":
        user = get_object_or_404(User, id=request.POST.get('userid'))
        form = UserCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commented_by = request.user
            comment.user = user
            comment.save()
            return JsonResponse({
                "comment_id": comment.id, "comment": comment.comment,
                "commented_on": comment.commented_on,
                "commented_by": comment.commented_by.email
            })
        return JsonResponse({"error": form.errors})


def edit_comment(request, pk):
    if request.method == "POST":
        comment_obj = get_object_or_404(Comment, id=pk)
        if request.user == comment_obj.commented_by:
            form = UserCommentForm(request.POST, instance=comment_obj)
            if form.is_valid():
                comment_obj.comment = form.cleaned_data.get("comment")
                comment_obj.save(update_fields=["comment"])
                return JsonResponse({
                    "comment_id": comment_obj.id,
                    "comment": comment_obj.comment,
                })
            return JsonResponse({"error": form['comment'].errors})
        data = {'error': "You don't have permission to edit this comment."}
        return JsonResponse(data)


def remove_comment(request):
    if request.method == "POST":
        comment_obj = get_object_or_404(
            Comment, id=request.POST.get('comment_id'))
        if request.user == comment_obj.commented_by:
            comment_obj.delete()
            data = {"cid": request.POST.get("comment_id")}
            return JsonResponse(data)
        data = {'error': "You don't have permission to delete this comment."}
        return JsonResponse(data)


def api_settings(request):
    api_settings = APISettings.objects.all()
    data = {'settings': api_settings}
    return render(request, 'settings/list.html', data)


def add_api_settings(request):
    users = User.objects.filter(is_active=True).order_by('email')
    form = APISettingsForm()
    if request.POST:
        form = APISettingsForm(request.POST)
        if form.is_valid():
            settings_obj = form.save(commit=False)
            settings_obj.created_by = request.user
            settings_obj.save()
            if request.POST.get('tags', ''):
                tags = request.POST.get("tags")
                splitted_tags = tags.split(",")
                for t in splitted_tags:
                    tag = Tags.objects.filter(name=t)
                    if tag:
                        tag = tag[0]
                    else:
                        tag = Tags.objects.create(name=t)
                    settings_obj.tags.add(tag)
            success_url = reverse_lazy("common:api_settings")
            if request.POST.get("savenewform"):
                success_url = reverse_lazy("common:add_api_settings")
            data = {'success_url': success_url, 'error': False}
            return JsonResponse(data)
        return JsonResponse({'error': True, 'errors': form.errors})
    data = {'form': form, "setting": api_settings,
            'users': users}
    return render(request, 'settings/create.html', data)


def view_api_settings(request, pk):
    api_settings = APISettings.objects.filter(pk=pk).first()
    data = {"setting": api_settings}
    return render(request, 'settings/view.html', data)


def update_api_settings(request, pk):
    api_settings = APISettings.objects.filter(pk=pk).first()
    users = User.objects.filter(is_active=True).order_by('email')
    form = APISettingsForm(instance=api_settings)
    if request.POST:
        form = APISettingsForm(
            request.POST, instance=api_settings)
        if form.is_valid():
            settings_obj = form.save(commit=False)
            settings_obj.save()
            if request.POST.get('tags', ''):
                settings_obj.tags.clear()
                tags = request.POST.get("tags")
                splitted_tags = tags.split(",")
                for t in splitted_tags:
                    tag = Tags.objects.filter(name=t)
                    if tag:
                        tag = tag[0]
                    else:
                        tag = Tags.objects.create(name=t)
                    settings_obj.tags.add(tag)
            success_url = reverse_lazy("common:api_settings")
            if request.POST.get("savenewform"):
                success_url = reverse_lazy("common:add_api_settings")
            data = {'success_url': success_url, 'error': False}
            return JsonResponse(data)
        return JsonResponse({'error': True, 'errors': form.errors})
    data = {
        'form': form, "setting": api_settings,
        'users': users,
    }
    return render(request, 'settings/update.html', data)


def delete_api_settings(request, pk):
    api_settings = APISettings.objects.filter(pk=pk).first()
    if api_settings:
        api_settings.delete()
        data = {"error": False, "response": "Successfully Deleted!"}
    else:
        data = {"error": True,
                "response": "Objeto No Encontrado!"}
    # return JsonResponse(data)
    return redirect('common:api_settings')


def change_passsword_by_admin(request):
    if request.user.role == "ADMIN" or request.user.is_superuser:
        if request.method == "POST":
            user = get_object_or_404(User, id=request.POST.get("useer_id"))
            user.set_password(request.POST.get("new_passwoord"))
            user.save()
            mail_subject = 'Contraseña de la cuenta fue cambiada'
            message = "<h3><b>hola</b> <i>" + user.username +\
                "</i></h3><br><h2><p> <b>Contraseña de la cuenta fue cambiada !\
                 </b></p></h2>" \
                + "<br> <p><b> Nueva contraseña</b> : <b><i>" + \
                request.POST.get("new_passwoord") + "</i><br></p>"
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()
            return HttpResponseRedirect('/users/list/')
    raise PermissionDenied


# Empresa --------------------------------------------
class EmpresasListView(AdminRequiredMixin, TemplateView):
    model = Empresa
    context_object_name = "empresas"
    template_name = "emp_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(EmpresasListView, self).get_context_data(**kwargs)
        context["empresas"] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateEmpresaView(AdminRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "emp_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.impuestos = Impuesto.objects.all()
        return super(CreateEmpresaView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateEmpresaView, self).get_form_kwargs()
        kwargs.update({"asignado_a": self.impuestos})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        address_form = AddressForm(request.POST)

        if form.is_valid() and address_form.is_valid():
            address_obj = address_form.save()
            empresa_obj = form.save(commit=False)
            empresa_obj.direccion = address_obj
            empresa_obj.save()

            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        empresa_obj = form.save(commit=False)
        if self.request.POST.getlist('asignado_a', []):
            empresa_obj.asignado_a.add(
                *self.request.POST.getlist('asignado_a'))
            asignado_a_list = self.request.POST.getlist('asignado_a')
            for asignado_a_impuesto in asignado_a_list:
                impuesto = get_object_or_404(Impuesto, pk=asignado_a_impuesto)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        if self.request.POST.get("savenewform"):
            return redirect("common:create_empresa")

        return redirect('common:empresas_list')

    def form_invalid(self, form):
        address_form = AddressForm(self.request.POST)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'empresa_errors': form.errors,
                                 'address_errors': address_form.errors})
        return self.render_to_response(
            self.get_context_data(form=form, address_form=address_form))

    def get_context_data(self, **kwargs):
        context = super(CreateEmpresaView, self).get_context_data(**kwargs)
        context["empresa_form"] = context["form"]
        context["impuestos"] = self.impuestos
        context["countries"] = COUNTRIES
        context["asignadoa_list"] = [
            int(i) for i in self.request.POST.getlist('asignado_a', []) if i]

        if "address_form" in kwargs:
            context["address_form"] = kwargs["address_form"]
        else:
            if self.request.POST:
                context["address_form"] = AddressForm(self.request.POST)
            else:
                context["address_form"] = AddressForm()
        print(context)
        return context

class EmpresaDetailView(AdminRequiredMixin, DetailView):
    model = Empresa
    context_object_name = "empresa"
    template_name = "emp_detail.html"

    def get_context_data(self, **kwargs):
        context = super(EmpresaDetailView, self).get_context_data(**kwargs)

        impuesto_assgn_list = [asignado_a.id for asignado_a in context['object'].asignado_a.all()]


        empresa_obj = self.object
        empresa_data = []

        assigned_data = []
        for each in context['empresa'].asignado_a.all():
            assigned_dict = {}
            assigned_dict['id'] = each.id
            assigned_dict['nombre'] = each.nombre
            assigned_data.append(assigned_dict)

        context.update({
            "empresa_obj": empresa_obj,
            "impuestos_asi": assigned_data
        })

        return context


class UpdateEmpresaView(LoginRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "emp_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.impuestos = Impuesto.objects.all()
        return super(UpdateEmpresaView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateEmpresaView, self).get_form_kwargs()
        kwargs.update({"asignado_a": self.impuestos})

        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        address_obj = self.object.direccion
        form = self.get_form()
        address_form = AddressForm(request.POST, instance=address_obj)
        if form.is_valid() and address_form.is_valid():
            addres_obj = address_form.save()
            empresa_obj = form.save(commit=False)
            empresa_obj.direccion = addres_obj
            empresa_obj.save()
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        asignado_a_ids = self.get_object().asignado_a.all().values_list(
            'id', flat=True)

        empresa_obj = form.save(commit=False)
        all_members_list = []

        if self.request.POST.getlist('asignado_a', []):
            asignado_de_impuestos = form.cleaned_data.get(
                'asignado_a').values_list('id', flat=True)
            all_members_list = list(
                set(list(asignado_de_impuestos)) - set(list(asignado_a_ids)))
            if all_members_list:
                for asignado_a_impuesto in all_members_list:
                    impuesto = get_object_or_404(Impuesto, id=asignado_a_impuesto)

            empresa_obj.asignado_a.clear()
            empresa_obj.asignado_a.add(
                *self.request.POST.getlist('asignado_a'))
        else:
            contact_obj.asignado_a.clear()


        if self.request.is_ajax():
            return JsonResponse({'error': False})
        return redirect("common:empresas_list")

    def form_invalid(self, form):
        address_obj = self.object.direccion
        address_form = AddressForm(
            self.request.POST, instance=address_obj)
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'empresas_errors': form.errors,
                                 'address_errors': address_form.errors})
        return self.render_to_response(
            self.get_context_data(form=form, address_form=address_form))

    def get_context_data(self, **kwargs):
        context = super(UpdateEmpresaView, self).get_context_data(**kwargs)
        context["empresa_obj"] = self.object
        context["impuestos"] = self.impuestos
        impuesto_assgn_list = [
            asignado_a.id for asignado_a in context["empresa_obj"].asignado_a.all()]

        context["address_obj"] = self.object.direccion
        context["empresa_form"] = context["form"]
        context["countries"] = COUNTRIES
        context["asignadoa_list"] = [
            int(i) for i in self.request.POST.getlist('asignado_a', []) if i]

        if "address_form" in kwargs:
            context["address_form"] = kwargs["address_form"]
        else:
            if self.request.POST:
                context["address_form"] = AddressForm(
                    self.request.POST, instance=context["address_obj"])
            else:
                context["address_form"] = AddressForm(
                    instance=context["address_obj"])
        return context


class EmpresaDeleteView(AdminRequiredMixin, DeleteView):
    model = Empresa

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("common:empresas_list")


# Impuestos --------------------------------------------
class ImpuestosListView(AdminRequiredMixin, TemplateView):
    model = Impuesto
    context_object_name = "impuestos"
    template_name = "imp_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ImpuestosListView, self).get_context_data(**kwargs)
        context["impuestos"] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateImpuestoView(AdminRequiredMixin, CreateView):
    model = Impuesto
    form_class = ImpuestoForm
    template_name = "imp_create.html"

    def get_form_kwargs(self):
        kwargs = super(CreateImpuestoView, self).get_form_kwargs()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        if form.is_valid():
            impuesto_obj = form.save(commit=False)
            impuesto_obj.save()

            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        impuesto_obj = form.save(commit=False)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        if self.request.POST.get("savenewform"):
            return redirect("common:create_impuesto")

        return redirect('common:impuestos_list')

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'impuesto_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CreateImpuestoView, self).get_context_data(**kwargs)
        context["impuesto_form"] = context["form"]

        return context

class ImpuestoDetailView(AdminRequiredMixin, DetailView):
    model = Impuesto
    context_object_name = "impuesto"
    template_name = "imp_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ImpuestoDetailView, self).get_context_data(**kwargs)

        impuesto_obj = self.object


        context.update({
            "impuesto_obj": impuesto_obj,
        })
        return context


class UpdateImpuestoView(LoginRequiredMixin, UpdateView):
    model = Impuesto
    form_class = ImpuestoForm
    template_name = "imp_create.html"

    def dispatch(self, request, *args, **kwargs):
        return super(UpdateImpuestoView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateImpuestoView, self).get_form_kwargs()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            empresa_obj = form.save(commit=False)
            empresa_obj.save()
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        empresa_obj = form.save(commit=False)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        return redirect("common:impuestos_list")

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'impuesto_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(UpdateImpuestoView, self).get_context_data(**kwargs)
        context["impuesto_obj"] = self.object
        context["impuesto_form"] = context["form"]

        return context


class ImpuestoDeleteView(AdminRequiredMixin, DeleteView):
    model = Impuesto

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("common:impuestos_list")

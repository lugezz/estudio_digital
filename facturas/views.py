import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View)
from common.models import User
from common.utils import COUNTRIES
from facturas.models import IVA
from facturas.forms import FacturasForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum


class FacturasListView(LoginRequiredMixin, TemplateView):
    model = IVA
    context_object_name = "facturas_obj_list"
    template_name = "facturas.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        if (self.request.user.role != "ADMIN" and not
                self.request.user.is_superuser):
            queryset = queryset.filter(
                Q(created_by=self.request.user))

        request_post = self.request.POST
        if request_post:
            if request_post.get('tipo_iva'):
                queryset = queryset.filter(
                    tipo_iva__icontains=request_post.get('tipo_iva'))
            if request_post.get('periodo'):
                queryset = queryset.filter(
                    periodo__icontains=request_post.get('periodo'))
            if request_post.get('neto_gravado'):
                queryset = queryset.filter(
                    neto_gravado__icontains=request_post.get('neto_gravado'))
            if request_post.get('neto_no_gravado'):
                queryset = queryset.filter(
                    neto_no_gravado__icontains=request_post.get('neto_no_gravado'))
            if request_post.get('exento'):
                queryset = queryset.filter(
                    exento__icontains=request_post.get('exento'))
            if request_post.get('iva'):
                queryset = queryset.filter(
                    iva__icontains=request_post.get('iva'))
            if request_post.get('percepcion'):
                queryset = queryset.filter(
                    percepcion__icontains=request_post.get('percepcion'))
            if request_post.get('total'):
                queryset = queryset.filter(
                    total__icontains=request_post.get('total'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(FacturasListView, self).get_context_data(**kwargs)
        context["facturas_obj_list"] = self.get_queryset()
        context["per_page"] = self.request.POST.get('per_page')
        context["users"] = User.objects.filter(
            is_active=True).order_by('email')
        search = False
        if (
            self.request.POST.get('tipo_iva') or
            self.request.POST.get('periodo')
        ):
            search = True
        context["search"] = search
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class ResultadosListView(LoginRequiredMixin, TemplateView):
    model = IVA
    context_object_name = "resultados_obj_list"
    template_name = "resultados.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        if (self.request.user.role != "ADMIN" and not
                self.request.user.is_superuser):
            queryset = queryset.filter(
                Q(created_by=self.request.user))

        request_post = self.request.POST


    def get_context_data(self, **kwargs):
        context = super(ResultadosListView, self).get_context_data(**kwargs)
        context["resultados_obj_list"] = self.get_queryset()
        context["per_page"] = self.request.POST.get('per_page')
        context["users"] = User.objects.filter(
            is_active=True).order_by('email')
        search = False
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateFacturaView(LoginRequiredMixin, CreateView):
    model = IVA
    form_class = FacturasForm
    template_name = "create_factura.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(CreateFacturaView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateFacturaView, self).get_form_kwargs()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            factura_obj = form.save(commit=False)
            factura_obj.created_by = self.request.user
            factura_obj.save()
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        factura_obj = form.save(commit=False)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        if self.request.POST.get("savenewform"):
            return redirect("facturas:add_factura")

        return redirect('facturas:list')

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'factura_errors': form.errors})
        return self.render_to_response(
            self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CreateFacturaView, self).get_context_data(**kwargs)
        context["factura_form"] = context["form"]
        context["users"] = self.users
        return context

class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = IVA
    context_object_name = "factura_record"
    template_name = "view_factura.html"

    def get_queryset(self):
        queryset = super(FacturaDetailView, self).get_queryset()
        return queryset.select_related("created_by")

    def get_context_data(self, **kwargs):
        context = super(FacturaDetailView, self).get_context_data(**kwargs)
        return context

class UpdateFacturaView(LoginRequiredMixin, UpdateView):
    model = IVA
    form_class = FacturasForm
    template_name = "create_factura.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.filter(is_active=True).order_by('email')
        return super(UpdateFacturaView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateFacturaView, self).get_form_kwargs()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            factura_obj = form.save(commit=False)
            factura_obj.created_by = self.request.user
            factura_obj.save()

            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        factura_obj = form.save(commit=False)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        return redirect("facturas:list")

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'factura_errors': form.errors})
        return self.render_to_response(
            self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(UpdateFacturaView, self).get_context_data(**kwargs)
        context["factura_obj"] = self.object
        context["factura_form"] = context["form"]
        context["users"] = self.users
        return context


class RemoveFacturaView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        self.object = get_object_or_404(id=id)
        if (self.request.user.role != "ADMIN" and not
            self.request.user.is_superuser and
                self.request.user != self.object.created_by):
            raise PermissionDenied
        else:
            self.object.delete()
            if self.request.is_ajax():
                return JsonResponse({'error': False})
            return redirect("facturas:list")

class GetFacturasView(LoginRequiredMixin, TemplateView):
    model = IVA
    context_object_name = "facturas"
    template_name = "facturas_list.html"

    def get_context_data(self, **kwargs):
        context = super(GetFacturasView, self).get_context_data(**kwargs)
        context["facturas"] = self.get_queryset()
        return context

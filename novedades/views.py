from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from common.models import User
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    ListView,
    DeleteView
)

from .forms import NovedadModelForm
from .models import Novedad

class NovedadCreateView(LoginRequiredMixin, CreateView):
    model = Novedad
    form_class = NovedadModelForm
    template_name = "novedad_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.all()
        return super(NovedadCreateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(NovedadCreateView, self).get_form_kwargs()
        kwargs.update({"asignado_a": self.users})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        if form.is_valid():
            novedad_obj = form.save(commit=False)
            novedad_obj.save()

            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        novedad_obj = form.save(commit=False)
        if self.request.POST.getlist('asignado_a', []):
            novedad_obj.asignado_a.add(
                *self.request.POST.getlist('asignado_a'))
            asignado_a_list = self.request.POST.getlist('asignado_a')
            for asignado_a_user in asignado_a_list:
                usuario = get_object_or_404(User, pk=asignado_a_user)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        if self.request.POST.get("savenewform"):
            return redirect("novedades:novedad-create")

        return redirect('novedades:novedad-list')

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'novedad_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(NovedadCreateView, self).get_context_data(**kwargs)
        context["novedad_form"] = context["form"]
        context["users"] = self.users
        context["asignadoa_list"] = [
            int(i) for i in self.request.POST.getlist('asignado_a', []) if i]

        return context

class NovedadListView(ListView):
    model = Novedad
    context_object_name = "Novedades"
    template_name = 'novedad_list.html'

    def get_queryset(self):
        queryset = self.model.objects.all()

        if self.request.user.role == "ADMIN" or self.request.user.is_superuser:
            pass
        else:
            queryset = queryset.filter(Q(asignado_a=self.request.user.id) | Q(asignado_a__isnull=True))

        return queryset

    def get_context_data(self, **kwargs):
        context = super(NovedadListView, self).get_context_data(**kwargs)
        context["novedades"] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

        # Filtrar por cliente

class NovedadDetailView(DetailView):
    model = Novedad
    context_object_name = "novedades"
    template_name = "novedad_detail.html"

    def get_context_data(self, **kwargs):
        context = super(NovedadDetailView, self).get_context_data(**kwargs)
        novedad_obj = self.object
        novedades_data = []
        context.update({"novedad_obj": novedad_obj})
        return context

class NovedadUpdateView(LoginRequiredMixin, UpdateView):
    model = Novedad
    form_class = NovedadModelForm
    template_name = "novedad_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.users = User.objects.all()
        return super(NovedadUpdateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(NovedadUpdateView, self).get_form_kwargs()
        kwargs.update({"asignado_a": self.users})

        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            novedad_obj = form.save(commit=False)
            novedad_obj.save()
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        asignado_a_ids = self.get_object().asignado_a.all().values_list(
            'id', flat=True)

        novedad_obj = form.save(commit=False)
        all_members_list = []

        if self.request.POST.getlist('asignado_a', []):
            asignado_de_users = form.cleaned_data.get(
                'asignado_a').values_list('id', flat=True)
            all_members_list = list(
                set(list(asignado_de_users)) - set(list(asignado_a_ids)))
            if all_members_list:
                for asignado_a_user in all_members_list:
                    novedad = get_object_or_404(Novedad, id=asignado_a_user)

            novedad_obj.asignado_a.clear()
            novedad_obj.asignado_a.add(
                *self.request.POST.getlist('asignado_a'))
        else:
            novedad_obj.asignado_a.clear()


        if self.request.is_ajax():
            return JsonResponse({'error': False})
        return redirect("novedades:novedad-list")

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'novedades_errors': form.errors})

        return self.render_to_response(
            self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(NovedadUpdateView, self).get_context_data(**kwargs)
        context["novedad_obj"] = self.object
        context["users"] = self.users
        novedad_assgn_list = [
            asignado_a.id for asignado_a in context["novedad_obj"].asignado_a.all()]

        imagen_name = str(context["novedad_obj"].imagen).split("/")
        imagen_name = imagen_name [-1]
        context["imagen_novedad"] = imagen_name

        context["novedad_form"] = context["form"]
        context["asignadoa_list"] = [
            int(i) for i in self.request.POST.getlist('asignado_a', []) if i]

        return context


class NovedadDeleteView(DeleteView):
    model = Novedad

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("novedades:novedad-list")

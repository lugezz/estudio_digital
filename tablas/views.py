from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View, DeleteView)
from tablib import Dataset
from import_export import mixins

from .models import *
from .forms import FeriadoForm
from .resources import FeriadoResource

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
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        feriados = Feriado.objects.all()
        ganart23 = GanArt23.objects.all()
        ganart90 = GanArt90.objects.all()

        context["feriados_count"] = feriados.count()
        context["ganart23_count"] = ganart23.count()
        context["ganart90_count"] = ganart90.count()

        return context

# Feriados --------------------------------------------
class FeriadosListView(AdminRequiredMixin, TemplateView):
    model = Feriado
    context_object_name = "feriados"
    template_name = "fer_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()

        request_post = self.request.POST

        if request_post and request_post.get('desde') != '':
            queryset = self.model.objects.filter(fecha__range=[request_post.get('desde'), request_post.get('hasta')])
            print (request_post.get('desde'))
            print (request_post.get('hasta'))
            print (queryset)
        return queryset


    def get_context_data(self, **kwargs):
        context = super(FeriadosListView, self).get_context_data(**kwargs)
        context["feriados"] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateFeriadoView(AdminRequiredMixin, CreateView):
    model = Feriado
    form_class = FeriadoForm
    template_name = "fer_create.html"

    def get_form_kwargs(self):
        kwargs = super(CreateFeriadoView, self).get_form_kwargs()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        if form.is_valid():
            feriado_obj = form.save(commit=False)
            feriado_obj.save()

            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        feriado_obj = form.save(commit=False)

        if self.request.is_ajax():
            return JsonResponse({'error': False})
        if self.request.POST.get("savenewform"):
            return redirect("tablas:feriado-create")

        return redirect('tablas:feriados-list')

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'feriado_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CreateFeriadoView, self).get_context_data(**kwargs)
        context["feriado_form"] = context["form"]

        return context

class FeriadoDetailView(AdminRequiredMixin, DetailView):
    model = Feriado
    context_object_name = "feriado"
    template_name = "fer_detail.html"

    def get_context_data(self, **kwargs):
        context = super(FeriadoDetailView, self).get_context_data(**kwargs)

        feriado_obj = self.object


        context.update({
            "feriado_obj": feriado_obj,
        })
        return context


class UpdateFeriadoView(LoginRequiredMixin, UpdateView):
    model = Feriado
    form_class = FeriadoForm
    template_name = "fer_create.html"

    def dispatch(self, request, *args, **kwargs):
        return super(UpdateFeriadoView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateFeriadoView, self).get_form_kwargs()
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
        return redirect("tablas:feriados-list")

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'feriado_errors': form.errors})
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(UpdateFeriadoView, self).get_context_data(**kwargs)
        context["feriado_obj"] = self.object
        context["feriado_form"] = context["form"]

        return context

class FeriadoDeleteView(AdminRequiredMixin, DeleteView):
    model = Feriado

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect("tablas:feriados-list")

def importar_feriado(request):
    #template = loader.get_template('export/importar.html')
    if request.method == 'POST':
        feriado_resource = FeriadoResource()
        dataset = Dataset()
        print(dataset)
        nuevos_feriados = request.FILES['xlsfile']
        print(nuevos_feriados)
        imported_data = dataset.load(nuevos_feriados.read())
        print(dataset)
        result = feriado_resource.import_data(dataset, dry_run=True) # Test the data import
        print(result.has_errors())
        if not result.has_errors():
            feriado_resource.import_data(dataset, dry_run=False) # Actually import now

    return render(request, 'fer_import.html')

#-----------------------------------------------------------------------

# Ganancia Art. 23 --------------------------------------------
class GanArt23ListView(AdminRequiredMixin, TemplateView):
    model = GanArt23
    context_object_name = "GanArt23"
    template_name = "g23_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(FeriadosListView, self).get_context_data(**kwargs)
        context["GanArt23"] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

#-----------------------------------------------------------------------

# Ganancia Art. 90 --------------------------------------------
class GanArt90ListView(AdminRequiredMixin, TemplateView):
    model = GanArt90
    context_object_name = "GanArt90"
    template_name = "g90_list.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(FeriadosListView, self).get_context_data(**kwargs)
        context["GanArt90"] = self.get_queryset()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

#-----------------------------------------------------------------------
# Importaciones -------------

def simple_upload(request):
    if request.method == 'POST':
        feriado_resource = FeriadoResource()
        dataset = Dataset()
        new_feriados = request.FILES['myfile']

        imported_data = dataset.load(new_feriados.read())
        result = feriado_resource.import_data(dataset, dry_run=True)  # Test the data import

        if not result.has_errors():
            feriado_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'core/simple_upload.html')

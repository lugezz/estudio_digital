from django.shortcuts import render, get_object_or_404
from django.urls import reverse
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


class NovedadCreateView(CreateView):
    template_name = 'novedad_create.html'
    form_class = NovedadModelForm
    queryset = Novedad.objects.all() # <blog>/<modelname>_list.html
    #success_url = '/'

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    #def get_success_url(self):
    #    return '/'

class NovedadListView(ListView):
    template_name = 'novedad_list.html'
    queryset = Novedad.objects.all() # <blog>/<modelname>_list.html


class NovedadDetailView(DetailView):
    template_name = 'novedad_detail.html'
    #queryset = novedad.objects.all()

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Novedad, id=id_)


class NovedadUpdateView(UpdateView):
    template_name = 'novedad_create.html'
    form_class = NovedadModelForm

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(novedad, id=id_)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class NovedadDeleteView(DeleteView):
    template_name = 'novedad_delete.html'

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(novedad, id=id_)

    def get_success_url(self):
        return reverse('novedades:novedad-list')

from django.shortcuts import render
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import SubscriberForm

# Create your views here.

class HomePageView(FormView):
    """View for the homepage that handles subscriber form with built-in FormView."""
    template_name = 'homepage/index.html'
    form_class = SubscriberForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Subscription successful!')
        return super().form_valid(form)

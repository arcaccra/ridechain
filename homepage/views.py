from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import SubscriberForm
from accounts.models import Subscriber

# Create your views here.

class HomePageView(View):
    """View for the homepage that handles subscriber form."""
    template_name = 'homepage/index.html'
    form_class = SubscriberForm
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        """Handles GET requests to display the subscriber form and list of subscribers."""
        form = self.form_class()
        subscribers = Subscriber.objects.all()  # Retrieve all subscribers
        return render(request, self.template_name, {'form': form, 'subscribers': subscribers})

    def post(self, request, *args, **kwargs):
        """Handles POST requests to process the subscriber form."""
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription successful!')
            return HttpResponseRedirect(self.success_url)
        else:
            subscribers = Subscriber.objects.all()
            return render(request, self.template_name, {'form': form, 'subscribers': subscribers})

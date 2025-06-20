from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import SubscriberForm
from accounts.models import Subscriber
import os
from django.conf import settings

# Create your views here.

class HomePageView(View):
    """View for the homepage that handles subscriber form."""
    template_name = 'homepage/index.html'
    form_class = SubscriberForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        """Prepares context data for rendering."""
        context = {
            'form': kwargs.get('form', self.form_class()),
            'subscribers': Subscriber.objects.all(),
        }

        image_dir_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'profiles')
        profile_images = []
        try:
            if os.path.exists(image_dir_path):
                profile_images = [
                    f'images/profiles/{f}' for f in os.listdir(image_dir_path)
                    if os.path.isfile(os.path.join(image_dir_path, f)) and not f.startswith('.')
                ]
        except Exception:
            pass  # Handle exceptions gracefully

        context['profile_images'] = profile_images
        return context

    def get(self, request, *args, **kwargs):
        """Handles GET requests to display the subscriber form and list of subscribers."""
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Handles POST requests to process the subscriber form."""
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription successful!')
            return HttpResponseRedirect(self.success_url)
        
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)

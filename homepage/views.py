from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import SubscriberForm
from accounts.models import Subscriber
import os
import random
from django.conf import settings

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

        image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'profiles')
        images = [image for image in os.listdir(image_path) if image.endswith('.jpeg')]
        subscriber_data = []

        for subscriber in subscribers:
            random_image = random.choice(images) if images else ''
            subscriber_data.append((subscriber, f'images/profiles/{random_image}'))

        return render(request, self.template_name, {
            'form': form,
            'subscriber_data': subscriber_data,
            'subscribers': subscribers
        })

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

import os
import random
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.forms import SubscriberForm
from accounts.models import Subscriber
from ridechain import settings
from utilities.mailing_and_messaging import SendMail

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
            subscriber = form.save(commit=False)  # Save the form and get the subscriber instance
            html_message = render_to_string('welcome_email.html', {'subscriber': subscriber})
            mailer = SendMail(
                subject='Welcome to RideChain',
                message='Thank you for subscribing to RideChain!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=False
            )
            mailer.send_html_mail(html_message)
            subscriber.save()
            messages.success(
                request,
                f'Welcome to RideChain, {subscriber.name}! We are excited to have you join our community. We will keep you updated. Thank you for subscribing!'
            )
            return redirect (self.success_url)
        else:
            messages.error(request, 'There was an error with your subscription. Please try again.')
            subscribers = Subscriber.objects.all()
            return render(request, self.template_name, {'form': form, 'subscribers': subscribers})
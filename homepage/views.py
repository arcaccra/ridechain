import random
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.forms import SubscriberForm
from accounts.models import Subscriber
from rides.models import Location
import os
import csv
import logging
from django.conf import settings
from utilities.mailing_and_messaging import SendMail

logger = logging.getLogger(__name__)


class ImportUniversityLocationsView(View):
    """View to handle the import of university locations from CSV."""

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """
        Handle GET request to import university locations from CSV.
        This endpoint processes the CSV file and creates/updates Location records.
        """
        try:
            file_path = os.path.join(settings.BASE_DIR, 'rides', 'locations.csv')

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Read the CSV file using DictReader for better column handling
                reader = csv.DictReader(csvfile)

                # Initialize counters
                created_count = 0
                updated_count = 0

                for row in reader:
                    # Clean and prepare the data
                    name = row.get('Name', '').strip()
                    if not name:
                        continue  # Skip rows without a name

                    # Handle GPS data (maybe 'N/A' or empty)
                    gps = row.get('Ghana Post GPS', '').strip()
                    if gps.upper() == 'N/A' or not gps:
                        gps = None

                    # Get coordinates with validation
                    try:
                        latitude = float(row.get('Latitude', 0))
                        longitude = float(row.get('Longitude', 0))
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid coordinates for {name}, skipping...")
                        continue

                    # Get category or use default
                    category = row.get('Category', 'University').strip()

                    # Create or update the location
                    _, created = Location.objects.update_or_create(
                        name=name,
                        defaults={
                            'ghana_post_gps': gps,
                            'latitude': latitude,
                            'longitude': longitude,
                            'category': category,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            # Prepare success message
            message = (
                f"Successfully imported {created_count} new locations. "
                f"Updated {updated_count} existing locations."
            )
            messages.success(request, message)

            # Return to the admin page or home
            return redirect('admin:rides_location_changelist')

        except FileNotFoundError:
            error_msg = "CSV file not found. Please ensure the file exists at 'rides/ghana_university_locations.csv'."
            logger.error(error_msg)
            messages.error(request, error_msg)
            return redirect('home')

        except Exception as e:
            error_msg = f"An error occurred during import: {str(e)}"
            logger.exception(error_msg)
            messages.error(request, "An error occurred while importing locations. Please check the logs for details.")
            return redirect('home')


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
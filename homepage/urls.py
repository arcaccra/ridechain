from django.urls import path
from homepage.views import HomePageView, ImportUniversityLocationsView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('import-university-locations/', ImportUniversityLocationsView.as_view(), name='import_university_locations'),
    # Add more URL patterns here as needed
]
from django.shortcuts import render
from django.views import View

# Create your views here.

class HomePageView(View):
    @staticmethod
    def get(request):
        return render(request, 'homepage/index.html')
    @staticmethod
    def post(request):
        # Handle form submission or other POST requests here
        return render(request, 'homepage/index.html')


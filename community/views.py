from django.shortcuts import render
from django.views import View

# Create your views here.

class CommunityView(View):
    def get(self, request):
        return render(request, 'community/community.html')


class BlogView(View):
    def get(self, request):
        return render(request, 'community/blog.html')

from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ApiRootView

urlpatterns = [
    path('', ApiRootView.as_view(), name='apis_root'),
    path('accounts/', include('apis.account_apis.urls')),
]
urlpatterns = format_suffix_patterns(urlpatterns)
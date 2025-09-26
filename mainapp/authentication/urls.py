from django.urls import path

from .views import RoleBasedLoginView

app_name = 'authentication'
urlpatterns = [
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('signup/', __import__('authentication.views', fromlist=['signup']).signup, name='signup'),
]

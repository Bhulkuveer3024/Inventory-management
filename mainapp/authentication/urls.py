from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import RoleBasedLoginView

app_name = 'authentication'
urlpatterns = [
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('signup/', __import__('authentication.views', fromlist=['signup']).signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='authentication:login'), name='logout'),
]

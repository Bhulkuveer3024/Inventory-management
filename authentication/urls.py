from django.urls import path
from .views import login_view, signup_view, logout_view, dashboard, home_view

app_name = 'authentication'
urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
]
from django.urls import path
from .views import login_view, signup_view, logout_view, dashboard

app_name = 'authentication'
urlpatterns = [
	path('login/', login_view, name='login'),
	path('signup/', signup_view, name='signup'),
	path('logout/', logout_view, name='logout'),
	path('dashboard/', dashboard, name='dashboard'),
]
from django.urls import path, include

app_name = 'authentication'
urlpatterns = []

from django.urls import path
from . import views

app_name = 'ttms_app'  # Important for namespace

urlpatterns = [
    # Dashboard URLs
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Optional alias
    
    # Other pages
    path('users/', views.users_view, name='users'),
    path('products/', views.products_view, name='products'),
    path('orders/', views.orders_view, name='orders'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
]
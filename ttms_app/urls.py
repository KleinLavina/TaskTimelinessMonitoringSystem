from django.urls import path
from . import views

app_name = 'ttms_app'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Employee CRUD
    path('users/', views.users_view, name='users'),
    path('users/add/', views.add_employee_view, name='add_employee'),
    path('users/edit/<int:id>/', views.edit_employee_view, name='edit_employee'),
    path('users/delete/<int:id>/', views.delete_employee_view, name='delete_employee'),
    path('users/get/<int:id>/', views.get_employee_data, name='get_employee_data'),
    
    
    # Other pages (add these if you have them)
    path('products/', views.products_view, name='products'),
    path('settings/', views.settings_view, name='settings'),
]
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
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/add/', views.add_task_view, name='add_task'),
    path('tasks/edit/<int:id>/', views.edit_task_view, name='edit_task'),
    path('tasks/delete/<int:id>/', views.delete_task_view, name='delete_task'),
    path('tasks/get/<int:id>/', views.get_task_data, name='get_task_data'),
    path('settings/', views.settings_view, name='settings'),
]
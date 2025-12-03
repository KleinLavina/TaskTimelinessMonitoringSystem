from datetime import datetime # Keep standard datetime if you need it

# ➡️ ADD THIS: Use Django's timezone utility
from django.utils import timezone 

from gettext import translation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Employee, Task, TaskAssignment

def dashboard_view(request):
    """Render the admin dashboard"""
    return render(request, 'admin_dashboard/dashboard.html')

def users_view(request):
    employees = Employee.objects.all().order_by('id')
    
    total_employees = employees.count()
    email_count = employees.filter(notification_preference='email').count()
    inapp_count = employees.filter(notification_preference='in_app').count()
    none_count = employees.filter(notification_preference='none').count()
    
    context = {
        'page_title': 'Employee Management',
        'employees': employees,
        'total_employees': total_employees,  # This should work
        'email_count': email_count,          # This should work
        'inapp_count': inapp_count,          # This should work
        'none_count': none_count,            # This should work
    }
    return render(request, 'admin_dashboard/employee.html', context)

def add_employee_view(request):
    """Add a new employee"""
    if request.method == 'POST':
        try:
            Employee.objects.create(
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                department=request.POST.get('department'),
                role=request.POST.get('role'),
                notification_preference=request.POST.get('notification_preference', 'email')
            )
            messages.success(request, 'Employee added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding employee: {str(e)}')
    
    return redirect('ttms_app:users')

def edit_employee_view(request, id):
    """Edit an existing employee"""
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == 'POST':
        try:
            employee.full_name = request.POST.get('full_name')
            employee.email = request.POST.get('email')
            employee.department = request.POST.get('department')
            employee.role = request.POST.get('role')
            employee.notification_preference = request.POST.get('notification_preference', 'email')
            employee.save()
            messages.success(request, f'{employee.full_name} updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
    
    return redirect('ttms_app:users')

def delete_employee_view(request, id):
    """Delete an employee"""
    if request.method == 'POST':
        employee = get_object_or_404(Employee, id=id)
        employee_name = employee.full_name
        employee.delete()
        messages.success(request, f'{employee_name} deleted successfully!')
    
    return redirect('ttms_app:users')

def get_employee_data(request, id):
    """Get employee data for editing (AJAX)"""
    employee = get_object_or_404(Employee, id=id)
    data = {
        'id': employee.id,
        'full_name': employee.full_name,
        'email': employee.email,
        'department': employee.department,
        'role': employee.role,
        'notification_preference': employee.notification_preference,
    }
    return JsonResponse(data)

# Add other views you might need

def tasks_view(request):
    """Task Definitions page view"""
    tasks = Task.objects.all().order_by('id')
    
    total_tasks = tasks.count()
    high_priority_count = tasks.filter(priority='high').count()
    medium_priority_count = tasks.filter(priority='medium').count()
    low_priority_count = tasks.filter(priority='low').count()
    
    context = {
        'page_title': 'Task Management',
        'tasks': tasks,
        'total_tasks': total_tasks,
        'high_priority_count': high_priority_count,
        'medium_priority_count': medium_priority_count,
        'low_priority_count': low_priority_count,
    }
    return render(request, 'admin_dashboard/tasks.html', context)

def add_task_view(request):
    """Add a new task definition"""
    if request.method == 'POST':
        try:
            Task.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                standard_duration_days=request.POST.get('standard_duration_days', 3),
                priority=request.POST.get('priority', 'medium')
            )
            messages.success(request, 'Task definition added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding task: {str(e)}')
    
    return redirect('ttms_app:tasks')

def edit_task_view(request, id):
    """Edit an existing task definition"""
    task = get_object_or_404(Task, id=id)
    
    if request.method == 'POST':
        try:
            task.title = request.POST.get('title')
            task.description = request.POST.get('description', '')
            task.standard_duration_days = request.POST.get('standard_duration_days', 3)
            task.priority = request.POST.get('priority', 'medium')
            task.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')
    
    return redirect('ttms_app:tasks')

def delete_task_view(request, id):
    """Delete a task definition"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=id)
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
    
    return redirect('ttms_app:tasks')

def get_task_data(request, id):
    """Get task data for editing (AJAX)"""
    task = get_object_or_404(Task, id=id)
    data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'standard_duration_days': task.standard_duration_days,
        'priority': task.priority,
    }
    return JsonResponse(data)

def tasks_assign_view(request):
    """Task Assignments page view"""
    assignments = TaskAssignment.objects.all().order_by('-required_due_date')
    
    total_assignments = assignments.count()
    overdue_count = assignments.filter(submission_status='D').count()
    in_progress_count = assignments.filter(submission_status='IP').count()
    completed_count = assignments.filter(submission_status__in=['OT', 'L']).count()
    pending_count = assignments.filter(submission_status='P').count()
    
    # Get available tasks and employees for the add modal
    available_tasks = Task.objects.all()
    available_employees = Employee.objects.all()
    
    context = {
        'page_title': 'Task Assignments',
        'assignments': assignments,
        'total_assignments': total_assignments,
        'overdue_count': overdue_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'available_tasks': available_tasks,
        'available_employees': available_employees,
        'now': timezone.now(),
    }
    return render(request, 'admin_dashboard/tasks_assign.html', context)


def settings_view(request):
    """settings page view"""
    return render(request, 'admin_dashboard/settings.html')
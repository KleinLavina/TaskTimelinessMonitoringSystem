from datetime import datetime # Keep standard datetime if you need it

# ➡️ ADD THIS: Use Django's timezone utility
from django.utils import timezone 

from gettext import translation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Employee, Task, TaskAssignment

def dashboard_view(request):
    """Render the admin dashboard"""
    return render(request, 'admin_dashboard/dashboard.html')

#==================EMPLOYEE PAGE=================
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

#=======================TASK PAGE=========================

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


#========================TASK ASSIGNMENT=====================
def assignments_view(request):
    assignments = TaskAssignment.objects.all().order_by('id')

    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        assignments = assignments.filter(submission_status=status_filter)

    context = {
        'assignments': assignments,
        'now': timezone.now(),
        'employees': Employee.objects.all(),
        'tasks': Task.objects.all()
    }

    return render(request, 'admin_dashboard/assignment.html', context)


def create_assignment_view(request):
    """Create TaskAssignment (workers + tasks + due date)"""
    if request.method == "POST":
        try:
            workers = request.POST.getlist("workers")
            tasks = request.POST.getlist("tasks")
            due_date = request.POST.get("required_due_date")

            assignment = TaskAssignment.objects.create(
                required_due_date=due_date
            )

            assignment.worker.set(workers)
            assignment.task.set(tasks)
            assignment.save()

            messages.success(request, "Task Assignment created successfully!")

        except Exception as e:
            messages.error(request, f"Error creating assignment: {str(e)}")

        return redirect('ttms_app:assignments')

    # fallback GET
    return redirect('ttms_app:assignments')


def settings_view(request):
    """settings page view"""
    return render(request, 'admin_dashboard/settings.html')
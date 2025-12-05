from datetime import datetime # Keep standard datetime if you need it

# ➡️ ADD THIS: Use Django's timezone utility
from django.utils import timezone 
from django.utils.timezone import make_aware

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

#====================================================EMPLOYEE PAGE=========================================================================
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

#===============================================================TASK PAGE================================================================================

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


#=================================================================================TASK ASSIGNMENT====================================================================
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
    """Create TaskAssignment with unique employee/task assignment"""
    if request.method == "POST":
        try:
            # Get form data
            worker_ids = request.POST.getlist("workers[]")
            task_ids = request.POST.getlist("tasks[]")
            due_date_str = request.POST.get("required_due_date")
            
            # Filter out empty values
            worker_ids = [w for w in worker_ids if w]
            task_ids = [t for t in task_ids if t]
            
            # Validate
            if not worker_ids:
                messages.error(request, "Please select at least one employee.")
                return redirect('ttms_app:assignments')
            
            if not task_ids:
                messages.error(request, "Please select at least one task.")
                return redirect('ttms_app:assignments')
            
            if not due_date_str:
                messages.error(request, "Please select a due date.")
                return redirect('ttms_app:assignments')
            
            # Check for duplicates (should be prevented by JS, but double-check)
            if len(worker_ids) != len(set(worker_ids)):
                messages.error(request, "Duplicate employees selected.")
                return redirect('ttms_app:assignments')
            
            if len(task_ids) != len(set(task_ids)):
                messages.error(request, "Duplicate tasks selected.")
                return redirect('ttms_app:assignments')
            
            # Convert date
            due_date = timezone.make_aware(
                datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            )
            
            if due_date <= timezone.now():
                messages.error(request, "Due date must be in the future.")
                return redirect('ttms_app:assignments')
            
            # Create assignment
            assignment = TaskAssignment.objects.create(
                required_due_date=due_date,
                submission_status='P'
            )
            
            # Add employees and tasks
            assignment.worker.add(*worker_ids)
            assignment.task.add(*task_ids)
            
            messages.success(request, 
                f"Assignment created successfully! {len(worker_ids)} employee(s) assigned to {len(task_ids)} task(s).")
            
        except Exception as e:
            messages.error(request, f"Error creating assignment: {str(e)}")
        
        return redirect('ttms_app:assignments')
    
    # GET request
    employees = Employee.objects.all().order_by('full_name')
    tasks = Task.objects.all().order_by('title')
    
    return render(request, 'admin_dashboard/assignment.html', {
        'employees': employees,
        'tasks': tasks,
    })

def settings_view(request):
    """settings page view"""
    return render(request, 'admin_dashboard/settings.html')
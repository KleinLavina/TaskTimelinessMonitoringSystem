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
    return render(request, 'admin_dashboard/task_assign.html', context)

def add_assignment_view(request):
    """Add a new task assignment"""
    if request.method == 'POST':
        try:
            # Get selected tasks and workers
            selected_task_ids = request.POST.getlist('tasks')
            selected_worker_ids = request.POST.getlist('workers')
            
            # Validate selections
            if not selected_task_ids:
                messages.error(request, 'Please select at least one task.')
                return redirect('ttms_app:assign')
            
            if not selected_worker_ids:
                messages.error(request, 'Please assign to at least one employee.')
                return redirect('ttms_app:assign')
            
            # Parse due date
            due_date_str = request.POST.get('required_due_date')
            required_due_date = datetime.fromisoformat(due_date_str)
            
            # Create assignment
            assignment = TaskAssignment.objects.create(
                required_due_date=required_due_date,
                submission_status=request.POST.get('submission_status', 'P')
            )
            
            # Add tasks and workers (ManyToMany relationships)
            assignment.task.set(selected_task_ids)
            assignment.worker.set(selected_worker_ids)
            
            # Save to trigger status logic
            assignment.save()
            
            messages.success(request, 'Task assignment created successfully!')
            
        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')
    
    return redirect('ttms_app:assign')

def edit_assignment_view(request, id):
    """Edit an existing task assignment"""
    assignment = get_object_or_404(TaskAssignment, id=id)
    
    if request.method == 'POST':
        try:
            with translation.atomic():
                # Update basic fields
                due_date_str = request.POST.get('required_due_date')
                if due_date_str:
                    assignment.required_due_date = datetime.fromisoformat(due_date_str)
                
                assignment.submission_status = request.POST.get('submission_status', 'P')
                
                # Update completion date if provided and status is OT or L
                completion_date_str = request.POST.get('actual_completion_date')
                if completion_date_str and assignment.submission_status in ['OT', 'L']:
                    assignment.actual_completion_date = datetime.fromisoformat(completion_date_str)
                elif assignment.submission_status not in ['OT', 'L']:
                    assignment.actual_completion_date = None
                
                # Update ManyToMany relationships
                selected_task_ids = request.POST.getlist('tasks')
                selected_worker_ids = request.POST.getlist('workers')
                
                if selected_task_ids:
                    assignment.task.set(selected_task_ids)
                
                if selected_worker_ids:
                    assignment.worker.set(selected_worker_ids)
                
                # Save to trigger status logic
                assignment.save()
                
                messages.success(request, f'Assignment #{assignment.id} updated successfully!')
                
        except Exception as e:
            messages.error(request, f'Error updating assignment: {str(e)}')
    
    return redirect('ttms_app:assign')

def delete_assignment_view(request, id):
    """Delete a task assignment"""
    if request.method == 'POST':
        assignment = get_object_or_404(TaskAssignment, id=id)
        assignment_id = assignment.id
        
        # Check if assignment can be deleted (only pending or in progress)
        if assignment.submission_status in ['OT', 'L']:
            messages.warning(request, f'Cannot delete completed assignment #{assignment_id}.')
            return redirect('ttms_app:assign')
        
        try:
            assignment.delete()
            messages.success(request, f'Assignment #{assignment_id} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting assignment: {str(e)}')
    
    return redirect('ttms_app:assign')

def complete_assignment_view(request, id):
    """Mark an assignment as complete"""
    if request.method == 'POST':
        assignment = get_object_or_404(TaskAssignment, id=id)
        
        try:
            with translation.atomic():
                # Set completion date
                completion_date_str = request.POST.get('actual_completion_date')
                if completion_date_str:
                    assignment.actual_completion_date = datetime.fromisoformat(completion_date_str)
                else:
                    assignment.actual_completion_date = timezone.now()
                
                # Save will automatically update status based on due date
                assignment.save()
                
                # Add completion notes if provided
                completion_notes = request.POST.get('completion_notes', '')
                if completion_notes:
                    # You might want to store this in a separate model
                    pass
                
                messages.success(request, f'Assignment #{assignment.id} marked as complete!')
                
        except Exception as e:
            messages.error(request, f'Error completing assignment: {str(e)}')
    
    return redirect('ttms_app:assign')

def get_assignment_data(request, id):
    """Get assignment data for editing/viewing (AJAX)"""
    try:
        assignment = get_object_or_404(TaskAssignment, id=id)
        
        # Get related tasks with their details
        tasks = assignment.task.all()
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'standard_duration_days': task.standard_duration_days,
            })
        
        # Get assigned workers
        workers = assignment.worker.all()
        workers_data = []
        for worker in workers:
            workers_data.append({
                'id': worker.id,
                'full_name': worker.full_name,
                'email': worker.email,
                'position': worker.role,
                'department': worker.department,
            })
        
        # Format dates for JavaScript
        assigned_date_iso = assignment.assigned_date.isoformat() if assignment.assigned_date else None
        due_date_iso = assignment.required_due_date.isoformat() if assignment.required_due_date else None
        completion_date_iso = assignment.actual_completion_date.isoformat() if assignment.actual_completion_date else None
        
        data = {
            'id': assignment.id,
            'assigned_date': assigned_date_iso,
            'required_due_date': due_date_iso,
            'actual_completion_date': completion_date_iso,
            'submission_status': assignment.submission_status,
            'get_status_display': assignment.get_submission_status_display(),
            'tasks': tasks_data,
            'workers': workers_data,
            'is_overdue': assignment.submission_status == 'D',
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def update_assignment_status_view(request, id):
    """Update assignment status (AJAX)"""
    if request.method == 'POST':
        assignment = get_object_or_404(TaskAssignment, id=id)
        
        try:
            new_status = request.POST.get('status')
            if new_status in dict(TaskAssignment.STATUS_CHOICES).keys():
                assignment.submission_status = new_status
                assignment.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status updated to {assignment.get_submission_status_display()}',
                    'new_status': assignment.submission_status,
                    'new_status_display': assignment.get_submission_status_display(),
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def bulk_update_assignments_view(request):
    """Bulk update assignments (e.g., mark multiple as complete)"""
    if request.method == 'POST':
        try:
            assignment_ids = request.POST.getlist('assignment_ids')
            action = request.POST.get('action')
            
            assignments = TaskAssignment.objects.filter(id__in=assignment_ids)
            
            if action == 'mark_complete':
                for assignment in assignments:
                    if assignment.submission_status in ['P', 'IP', 'D']:
                        assignment.actual_completion_date = timezone.now()
                        assignment.save()
                
                messages.success(request, f'{len(assignments)} assignments marked as complete!')
                
            elif action == 'mark_in_progress':
                assignments.filter(submission_status='P').update(submission_status='IP')
                messages.success(request, f'Assignments marked as in progress!')
                
            elif action == 'delete':
                # Only delete pending/in progress assignments
                deletable = assignments.filter(submission_status__in=['P', 'IP'])
                count = deletable.count()
                deletable.delete()
                messages.success(request, f'{count} assignments deleted!')
            
        except Exception as e:
            messages.error(request, f'Error in bulk operation: {str(e)}')
    
    return redirect('ttms_app:assign')

def settings_view(request):
    """settings page view"""
    return render(request, 'admin_dashboard/settings.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Employee

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
    return render(request, 'admin_dashboard/users.html', context)

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
def products_view(request):
    """Products page view"""
    return render(request, 'admin_dashboard/products.html')



def settings_view(request):
    """settings page view"""
    return render(request, 'admin_dashboard/settings.html')
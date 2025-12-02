from django.contrib import admin
from .models import Employee, Task, TaskAssignment, SystemAlert, PerformanceMetric

# --- Custom Admin Classes ---

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'department', 'role', 'notification_preference')
    search_fields = ('full_name', 'email', 'department')
    list_filter = ('department', 'notification_preference')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'standard_duration_days', 'id')
    search_fields = ('title', 'description')
    list_filter = ('priority',)
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        ('Scheduling Defaults', {'fields': ('priority', 'standard_duration_days')}),
    )

# ----------------------------------------------------
# TaskAssignment Admin with ManyToMany Inlines
# ----------------------------------------------------

# Inline for Workers (M2M)
class WorkerInline(admin.TabularInline):
    # This automatically handles the many-to-many relationship table
    model = TaskAssignment.worker.through
    extra = 1 # Number of extra forms to display

# Inline for Tasks (M2M)
class TaskInline(admin.TabularInline):
    # This automatically handles the many-to-many relationship table
    model = TaskAssignment.task.through
    extra = 1

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 
        'assigned_date', 
        'required_due_date', 
        'actual_completion_date', 
        'submission_status'
    )
    search_fields = ('required_due_date',)
    list_filter = ('submission_status',)
    
    # Crucial for M2M fields: Use inlines instead of 'fields' or 'readonly_fields'
    inlines = [WorkerInline, TaskInline] 

    # Fields displayed on the main form, excluding the M2M fields managed by inlines
    fieldsets = (
        (None, {'fields': ('assigned_date', 'required_due_date', 'actual_completion_date')}),
        ('Status', {'fields': ('submission_status',)}),
    )
    
    # This makes the save method logic (status updates) run when saving in the admin.
    save_on_top = True


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'alert_type', 'trigger_datetime', 'is_sent')
    list_filter = ('alert_type', 'is_sent')
    search_fields = ('assignment__id', 'assignment__worker__full_name') # Search through related models
    readonly_fields = ('trigger_datetime', 'sent_datetime')


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('worker', 'on_time_percentage', 'total_tasks_completed', 'calculation_date')
    readonly_fields = ('calculation_date', 'total_tasks_completed', 'on_time_tasks_count', 'on_time_percentage')
    list_filter = ('calculation_date',)
    search_fields = ('worker__full_name',)
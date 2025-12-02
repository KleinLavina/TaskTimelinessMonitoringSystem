from django.db import models
from django.utils import timezone
from datetime import timedelta

# --- 1. Employee Model (Worker) ---
class Employee(models.Model):
    # Basic identification
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    
    # Organizational structure (simplified)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Notification preference (e.g., 'email', 'sms', 'in-app')
    notification_preference = models.CharField(
        max_length=10, 
        choices=[('email', 'Email'), ('in_app', 'In-App'), ('none', 'None')], 
        default='email'
    )

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
        
    def __str__(self):
        # FIX: Changed self.name to self.full_name to match the field name
        return self.full_name

# --- 2. Task Model (Definition) ---
class Task(models.Model):
    # Definition of the work
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Standard time expected for completion (used for calculating RequiredDueDate)
    standard_duration_days = models.PositiveSmallIntegerField(
        default=3, 
        help_text="Standard number of days for task completion."
    )
    priority = models.CharField(
        max_length=10, 
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], 
        default='medium'
    )

    class Meta:
        verbose_name = "Task Definition"
        verbose_name_plural = "Task Definitions"
        
    def __str__(self):
        return self.title
    
# --- 3. TaskAssignment Model (The Core Tracking Model) ---
class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('IP', 'In Progress'),
        ('OT', 'On Time Completed'),
        ('L', 'Late Completed'),
        ('D', 'Overdue'),
    ]
    
    # CHANGE: Changed to ManyToManyField to allow one assignment to contain multiple workers.
    # The related_name is changed to 'assigned_tasks' for clarity.
    worker = models.ManyToManyField(Employee, related_name='assigned_tasks')
    
    # Already ManyToManyField to allow multiple tasks in one assignment
    task = models.ManyToManyField(Task, related_name='assignments')
    
    # Deadline and status tracking
    assigned_date = models.DateTimeField(default=timezone.now)
    # The ultimate deadline for all tasks within this assignment. Set manually.
    required_due_date = models.DateTimeField(
        help_text="The ultimate deadline for all tasks within this assignment."
    ) 
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    
    # Submission status
    submission_status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='P')
    
    class Meta:
        ordering = ['required_due_date']
        verbose_name = "Task Assignment"
        
    def save(self, *args, **kwargs):
        # The due date logic is preserved: status is updated based on completion time vs. required due date.
        
        # 2. Update status if completed
        if self.actual_completion_date and self.submission_status not in ('OT', 'L'):
            if self.actual_completion_date <= self.required_due_date:
                self.submission_status = 'OT' # On Time
            else:
                self.submission_status = 'L'  # Late
        
        # 3. Handle overdue status (updated if save is called while pending/in progress)
        elif self.submission_status in ('P', 'IP') and self.required_due_date < timezone.now():
            self.submission_status = 'D' # Overdue

        super().save(*args, **kwargs)
        
    def __str__(self):
        # Adjusted __str__ for M2M: Using 'pk' for ID, as querying worker names in __str__ is inefficient.
        return f"Assignment #{self.pk} (Collaborative)"
    
# --- 4. SystemAlert Model ---
class SystemAlert(models.Model):
    ALERT_TYPES = [
        ('WARN', 'Deadline Warning'),
        ('DUE', 'Deadline Today'),
        ('LATE', 'Overdue Notification'),
        ('CONF', 'Submission Confirmation'),
    ]

    assignment = models.ForeignKey(TaskAssignment, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=4, choices=ALERT_TYPES)
    message = models.TextField()
    
    # Tracking sent status
    trigger_datetime = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)
    sent_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "System Alert"
        
    def __str__(self):
        # CHANGE: Using self.assignment to access the descriptive __str__ of the related object
        return f"{self.get_alert_type_display()} for {self.assignment}"
    
# --- 5. PerformanceMetric Model (for Dashboard) ---
class PerformanceMetric(models.Model):
    # Link to the entity being measured (Worker or Department)
    worker = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    
    calculation_date = models.DateField(auto_now=True)
    
    # Key Metrics for the Dashboard
    total_tasks_completed = models.PositiveIntegerField(default=0)
    on_time_tasks_count = models.PositiveIntegerField(default=0)
    
    # This field stores the percentage for direct display (e.g., 85.5)
    on_time_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Performance Metric"
        
    def __str__(self):
        worker_name = self.worker.full_name if self.worker else 'N/A (Department Level)'
        return f"Metrics for {worker_name} calculated on {self.calculation_date}"
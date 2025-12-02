from django.shortcuts import render

def dashboard_view(request):
    """Main dashboard view"""
    context = {
        'page_title': 'Dashboard Overview',
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

def users_view(request):
    """Users page view"""
    context = {
        'page_title': 'User Management',
    }
    return render(request, 'admin_dashboard/users.html', context)

def products_view(request):
    """Products page view"""
    context = {
        'page_title': 'Product Management',
    }
    return render(request, 'admin_dashboard/products.html', context)

def orders_view(request):
    """Orders page view"""
    context = {
        'page_title': 'Order Management',
    }
    return render(request, 'admin_dashboard/orders.html', context)

def analytics_view(request):
    """Analytics page view"""
    context = {
        'page_title': 'Analytics',
    }
    return render(request, 'admin_dashboard/analytics.html', context)

def settings_view(request):
    """Settings page view"""
    context = {
        'page_title': 'Settings',
    }
    return render(request, 'admin_dashboard/settings.html', context)

def logout_view(request):
    """Logout view"""
    # Add your logout logic here
    from django.shortcuts import redirect
    from django.contrib.auth import logout
    
    logout(request)
    return redirect('ttms_app:dashboard')
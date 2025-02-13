# from django.shortcuts import render

# # Create your views here.
# def home(request):
#     return render(request, 'home.html')

from django.shortcuts import render, redirect
from .models import QueueItem

def home(request):
    if request.method == 'POST':
        order_data = {
            'customer_name': request.POST.get('customer_name'),
            'food_item': request.POST.get('food_item'),
            'quantity': request.POST.get('quantity')
        }
        QueueItem.push(order_data)
        return redirect('queue_app:home')  # Update this line
    
    queue_items = QueueItem.objects.filter(processed=False).order_by('created_at')
    return render(request, 'home.html', {'queue_items': queue_items})
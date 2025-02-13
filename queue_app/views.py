# from django.shortcuts import render

# # Create your views here.
# def home(request):
#     return render(request, 'home.html')

from django.shortcuts import render, redirect
from .models import QueueItem
import json

def home(request):
    if request.method == 'POST':
        order_data = {
            'customer_name': request.POST.get('customer_name'),
            'food_item': request.POST.get('food_item'),
            'quantity': request.POST.get('quantity')
        }
        queue_item = QueueItem.push(order_data)
        return redirect('queue_app:order_confirmation', order_id=queue_item.id)
    
    queue_items = QueueItem.objects.filter(processed=False).order_by('created_at')
    return render(request, 'home.html', {'queue_items': queue_items})

def order_confirmation(request, order_id):
    try:
        order = QueueItem.objects.get(id=order_id)
        # Get position in queue (count of unprocessed orders created before this one)
        position = QueueItem.objects.filter(
            processed=False,
            created_at__lte=order.created_at
        ).count()
        
        return render(request, 'order_confirmation.html', {
            'order': json.loads(order.data),
            'position': position,
            'created_at': order.created_at
        })
    except QueueItem.DoesNotExist:
        return redirect('queue_app:home')
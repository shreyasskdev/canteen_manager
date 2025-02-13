from django.shortcuts import render, redirect
import json
from .models import QueueItem

def home(request):
    if request.method == 'POST':
        order_data = {
            'customer_name': request.POST.get('customer_name'),
            'food_item': request.POST.get('food_item'),
            'quantity': request.POST.get('quantity')
        }
        # Save the order and store its ID in session for later reference.
        order = QueueItem.push(order_data)
        request.session['order_id'] = order.id
        return redirect('/queue')  # Redirect to the queue view
    return render(request, 'home.html')

def queue_view(request):
    # Retrieve the order id from session.
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('/')  # If no order found, send back to home
    
    try:
        order = QueueItem.objects.get(id=order_id)
    except QueueItem.DoesNotExist:
        return redirect('/')
    
    # Determine the current queue position:
    pending_orders = list(QueueItem.objects.filter(processed=False).order_by('created_at'))
    try:
        # Find the index of the current order (list index starts at 0, so add 1).
        position = pending_orders.index(order) + 1
    except ValueError:
        position = 'Processed'
    
    # Decode the stored JSON data for display.
    order_data = json.loads(order.data)
    
    return render(request, 'queue.html', {
        'order': order,
        'order_data': order_data,
        'position': position
    })

def pop_queue(request):
    context = {}
    if request.method == 'POST':
        # Call the pop method to get and remove the next unprocessed order.
        popped_data = QueueItem.pop()
        if popped_data:
            context['popped'] = popped_data
        else:
            context['message'] = 'No orders to pop.'
    return render(request, 'pop_queue.html', context)
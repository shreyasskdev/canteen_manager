# from django.shortcuts import render, redirect
# import json
# from .models import QueueItem

# from django.shortcuts import render, get_object_or_404
# import json
# from django.utils.timezone import now

from django.shortcuts import render, redirect, get_object_or_404
import json
from .models import QueueItem

# def home(request):
#     if request.method == 'POST':
#         order_data = {
#             'customer_name': request.POST.get('customer_name'),
#             'food_item': request.POST.get('food_item'),
#             'quantity': request.POST.get('quantity')
#         }
#         # Save the order and store its ID in session for later reference.
#         order = QueueItem.push(order_data)
#         request.session['order_id'] = order.id
#         return redirect('/queue')  # Redirect to the queue view
    
#     # Get all unprocessed queue items
#     queue_items = QueueItem.objects.filter(processed=False).order_by('created_at')
#     return render(request, 'home.html', {'queue_items': queue_items})
def home(request):
    if request.method == 'POST':
        # Collect form data
        customer_name = request.POST.get('customer_name')
        food_items = request.POST.getlist('food_items[]')
        quantities = request.POST.getlist('quantities[]')

        # Create order data structure
        order_data = {
            'customer_name': customer_name,
            'food_items': [
                {'name': food, 'quantity': int(qty)}
                for food, qty in zip(food_items, quantities)
            ]
        }

        # Save to queue
        order = QueueItem.push(order_data)
        request.session['order_id'] = order.id
        return redirect('/queue')

    # Existing GET handling remains the same
    queue_items = QueueItem.objects.filter(processed=False).order_by('created_at')
    return render(request, 'home.html', {'queue_items': queue_items})

# def queue_view(request):
#     # Retrieve the order id from session.
#     order_id = request.session.get('order_id')
#     if not order_id:
#         return redirect('/')  # If no order found, send back to home
    
#     try:
#         order = QueueItem.objects.get(id=order_id)
#     except QueueItem.DoesNotExist:
#         return redirect('/')
    
#     # Determine the current queue position:
#     pending_orders = list(QueueItem.objects.filter(processed=False).order_by('created_at'))
#     try:
#         # Find the index of the current order (list index starts at 0, so add 1).
#         position = pending_orders.index(order) + 1
#     except ValueError:
#         position = 'Processed'
    
#     # Decode the stored JSON data for display.
#     order_data = json.loads(order.data)
    
#     return render(request, 'queue.html', {
#         'order': order,
#         'order_data': order_data,
#         'position': position
#     })
from django.utils import timezone
from datetime import timedelta

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
    pending_orders = list(QueueItem.objects.filter(processed=False, cancelled=False).order_by('created_at'))
    try:
        # Find the index of the current order (list index starts at 0, so add 1).
        position = pending_orders.index(order) + 1
    except ValueError:
        position = 'Processed'
    
    # Decode the stored JSON data for display.
    order_data = json.loads(order.data)
    
    # Define the average processing time per order (in minutes)
    avg_processing_time_per_order = 4  # Example: 10 minutes per order
    
    # Calculate ETA in minutes
    if order.processed:
        eta = "Completed"
    else:
        # Calculate the total estimated time based on position
        estimated_minutes = position * avg_processing_time_per_order
        eta = f"{estimated_minutes}min"
    
    # Calculate waiting time
    if order.processed:
        waiting_time = "Completed"
    else:
        delta = timezone.now() - order.created_at
        minutes = int(delta.total_seconds() / 60)
        waiting_time = f"{minutes} minutes"
    
    return render(request, 'queue.html', {
        'order': order,
        'order_data': order_data,
        'position': position,
        'waiting_time': waiting_time,  # Pass waiting time to the template
        'eta': eta,  # Pass ETA to the template
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

def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(QueueItem, id=order_id)
    if not order.processed and not order.cancelled:
        QueueItem.cancel_order(order_id)
        # Optionally, you can add a success message here
    return redirect('/queue')

# def cancel_order(request, order_id):
#     """Cancel an order by marking it as processed"""
#     order = get_object_or_404(QueueItem, id=order_id)
#     if not order.processed:
#         order.processed = True
#         order.save()
#         # Optionally, add a success message here
#     return redirect('queue_app:queue')

# def calculate_queue_position(order):
#     """
#     Calculate the position of the order in the queue.
#     Assumes orders are processed in the order they were created.
#     """
#     # Count how many unprocessed orders were created before this one
#     return QueueItem.objects.filter(
#         created_at__lt=order.created_at,
#         processed=False
#     ).count() + 1  # Add 1 because the current order is also in the queue

# def calculate_estimated_time(position):
#     """
#     Calculate the estimated waiting time based on the queue position.
#     Each order takes 5 minutes to prepare (adjust as needed).
#     """
#     preparation_time_per_order = 5  # in minutes
#     return position * preparation_time_per_order

# def order_detail_view(request, order_id):
#     # Fetch the order
#     order = get_object_or_404(QueueItem, id=order_id)

#     # Parse order data
#     try:
#         order_data = json.loads(order.data)
#     except json.JSONDecodeError:
#         order_data = {'customer_name': 'Unknown', 'food_items': []}

#     # Calculate queue position
#     position = calculate_queue_position(order)

#     # Calculate estimated waiting time
#     estimated_time = calculate_estimated_time(position)

#     # Pass data to the template
#     context = {
#         'order': order,
#         'order_data': order_data,
#         'position': position,
#         'estimated_time': estimated_time,
#     }
#     return render(request, 'your_template.html', context)
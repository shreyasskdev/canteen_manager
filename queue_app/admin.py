from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import QueueItem

@admin.register(QueueItem)
class QueueItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_order_details', 'get_status_badge', 'waiting_time', 'created_at')
    list_filter = ('processed', 'created_at')
    search_fields = ('data',)
    ordering = ('-created_at',)
    actions = ['mark_as_processed', 'mark_as_unprocessed']
    
    def get_order_details(self, obj):
        import json
        data = json.loads(obj.data)
        return format_html(
            '<strong>Customer:</strong> {}<br>'
            '<strong>Item:</strong> {} (Qty: {})',
            data.get('customer_name', ''),
            data.get('food_item', ''),
            data.get('quantity', '')
        )
    get_order_details.short_description = 'Order Details'
    
    def get_status_badge(self, obj):
        if obj.processed:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 10px;">Completed</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; '
                'border-radius: 10px;">Pending</span>'
        )
    get_status_badge.short_description = 'Status'

    def waiting_time(self, obj):
        if obj.processed:
            return "Completed"
        delta = timezone.now() - obj.created_at
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes} minutes"
    waiting_time.short_description = 'Waiting Time'

    def mark_as_processed(self, request, queryset):
        queryset.update(processed=True)
    mark_as_processed.short_description = "Mark selected orders as completed"

    def mark_as_unprocessed(self, request, queryset):
        queryset.update(processed=False)
    mark_as_unprocessed.short_description = "Mark selected orders as pending"

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

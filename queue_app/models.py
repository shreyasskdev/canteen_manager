from django.db import models, transaction
import json
from django.utils import timezone

class QueueItem(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['processed', 'created_at']),
        ]
        ordering = ['created_at']

    @classmethod
    def push(cls, data):
        """Add item to queue"""
        json_data = json.dumps(data)
        return cls.objects.create(data=json_data)

    @classmethod
    def pop(cls):
        """Get and remove next item from queue"""
        # Use select_for_update() to prevent race conditions in concurrent environments
        with transaction.atomic():
            item = (cls.objects
                   .select_for_update()
                   .filter(processed=False)
                   .first())
            
            if item:
                item.processed = True
                item.save()
                return json.loads(item.data)
            return None

    @classmethod
    def peek(cls):
        """View next item without removing it"""
        item = cls.objects.filter(processed=False).first()
        return json.loads(item.data) if item else None

    @classmethod
    def clear(cls):
        """Clear all items from queue"""
        cls.objects.all().delete()

    @classmethod
    def size(cls):
        """Get number of unprocessed items in queue"""
        return cls.objects.filter(processed=False).count()

    def __str__(self):
        """String representation of the queue item"""
        return f"Queue Item {self.id} ({'Processed' if self.processed else 'Pending'})"

from django.db import models
from django.utils import timezone

class BOMComparison(models.Model):
    master_filename = models.CharField(max_length=255)
    user_filename = models.CharField(max_length=255)

    # JSONField (works with PostgreSQL, MySQL 5.7+, and SQLite 3.9+)
    master_data = models.JSONField(null=True, blank=True)
    user_data = models.JSONField(null=True, blank=True)
    comparison_result = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comparison: {self.master_filename} vs {self.user_filename} ({self.created_at:%Y-%m-%d %H:%M})"

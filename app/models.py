# models.py
from django.db import models
from django.utils import timezone

# models.py
from django.db import models
from django.utils import timezone

class CertificateRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    REJECT_REASON_CHOICES = (
        ('invalid_certificate', 'Invalid Certificate'),
        ('document_not_clear', 'Document Not Clear'),
        ('information_mismatch', 'Information Mismatch'),
        ('certificate_expired', 'Certificate Expired'),
        ('duplicate_request', 'Duplicate Request'),
        ('other', 'Other Reason'),
    )
    
    reg_id = models.CharField(max_length=20)
    user_name = models.CharField(max_length=100)
    certificate_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Admin fields
    admin_remarks = models.TextField(blank=True, null=True)
    blockchain_hash = models.CharField(max_length=200, blank=True, null=True)
    certificate_file = models.FileField(upload_to='certificates/%Y/%m/%d/', blank=True, null=True)
    
    # Rejection fields
    reject_reason = models.CharField(max_length=50, choices=REJECT_REASON_CHOICES, blank=True, null=True)
    reject_details = models.TextField(blank=True, null=True)
    
    # Dates
    request_date = models.DateTimeField(default=timezone.now)
    accepted_date = models.DateTimeField(blank=True, null=True)
    rejected_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-request_date']
        db_table = "CertificateRequest"
    
    def __str__(self):
        return f"{self.user_name} ({self.reg_id}) - {self.certificate_name} [{self.status}]"
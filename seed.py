"""
Quick seed script for demo data.
Run with: python manage.py shell < seed.py
"""
from django.contrib.auth import get_user_model
from crm.models import PipelineStage, LeadSource

User = get_user_model()

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@evcrm.local", "Admin@123", role="ADMIN")
    print("Created superuser: admin / Admin@123")

stages = [
    ("New Lead", 1, False, False),
    ("Contacted", 2, False, False),
    ("Qualified", 3, False, False),
    ("Proposal/Quotation", 4, False, False),
    ("Negotiation", 5, False, False),
    ("Won", 6, True, False),
    ("Lost", 7, False, True),
]
for name, order, is_won, is_lost in stages:
    PipelineStage.objects.get_or_create(name=name, defaults={"order": order, "is_won": is_won, "is_lost": is_lost})

for src in ["Website", "Referral", "Walk-in", "Social Media", "Cold Call", "Exhibition"]:
    LeadSource.objects.get_or_create(name=src)

print("Seed data ready.")

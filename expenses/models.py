from django.db import models
from account.models import Account

# Create your models here.
class Expense(models.Model):

  CATEGORY_OPTIONS = (
    ('ONLINE_SERVICES', 'ONLINE_SERVICES'),
    ('TRAVEL', 'TRAVEL'),
    ('FOOD', 'FOOD'),
    ('RENT', 'RENT'),
    ('OTHERS', 'OTHERS'),
  )

  category = models.CharField(max_length=80, choices=CATEGORY_OPTIONS)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  description = models.TextField()
  owner = models.ForeignKey(to=Account, on_delete=models.CASCADE)
  date = models.DateField(null=False, blank=False)

  def __str__(self):
    return self.owner.username

  class Meta:
    ordering = ['-date']

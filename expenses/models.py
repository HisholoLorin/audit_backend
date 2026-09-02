from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default='')  # lucide icon name
    color = models.CharField(max_length=7, blank=True, default='#6366f1')  # hex color
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        unique_together = ['name', 'user']
        ordering = ['name']

    def __str__(self):
        return self.name

class MonthlyIncome(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField(help_text='First day of the month')  # Always store as YYYY-MM-01
    source = models.CharField(max_length=100, blank=True, default='', help_text='e.g. Salary, Freelance, Bonus')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'monthly incomes'
        ordering = ['-month', '-created_at']

    def __str__(self):
        label = f' ({self.source})' if self.source else ''
        return f'{self.user.username} - {self.month.strftime("%B %Y")}{label} - {self.amount}'

class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.title} - {self.amount}'

class BreakdownCluster(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='clusters')
    name = models.CharField(max_length=200)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'created_at']

    def __str__(self):
        return f'{self.name} - {self.date}'

class ExpenseBreakdown(models.Model):
    cluster = models.ForeignKey(BreakdownCluster, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        qty = f' ({self.quantity})' if self.quantity else ''
        return f'{self.name}{qty} - {self.amount}'

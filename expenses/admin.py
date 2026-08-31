from django.contrib import admin
from .models import Category, MonthlySalary, Expense

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'icon', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)

@admin.register(MonthlySalary)
class MonthlySalaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'amount', 'created_at')
    list_filter = ('user', 'month')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'category', 'user')
    list_filter = ('user', 'category', 'date')
    search_fields = ('title', 'description')

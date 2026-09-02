from rest_framework import serializers
from .models import Category, MonthlyIncome, Expense, BreakdownCluster, ExpenseBreakdown
from datetime import date

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class MonthlyIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyIncome
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate_month(self, value):
        if value.day != 1:
            raise serializers.ValidationError("Month must be the first day of the month.")
        return value

class ExpenseBreakdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseBreakdown
        fields = '__all__'
        read_only_fields = ('cluster', 'created_at',)

class BreakdownClusterSerializer(serializers.ModelSerializer):
    items = ExpenseBreakdownSerializer(many=True, read_only=True)

    class Meta:
        model = BreakdownCluster
        fields = '__all__'
        read_only_fields = ('expense', 'created_at',)

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    clusters = BreakdownClusterSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

from rest_framework import viewsets, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from .models import Category, MonthlySalary, Expense
from .serializers import CategorySerializer, MonthlySalarySerializer, ExpenseSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MonthlySalaryViewSet(viewsets.ModelViewSet):
    serializer_class = MonthlySalarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = MonthlySalary.objects.filter(user=self.request.user)
        month = self.request.query_params.get('month', None)
        if month:
            try:
                date_obj = datetime.strptime(month, '%Y-%m').date()
                queryset = queryset.filter(month=date_obj)
            except ValueError:
                pass
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        month = self.request.query_params.get('month')
        if month:
            try:
                date_obj = datetime.strptime(month, '%Y-%m').date()
                queryset = queryset.filter(date__year=date_obj.year, date__month=date_obj.month)
            except ValueError:
                pass
                
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        current_month = today.replace(day=1)
        
        # Current month salary
        salary_obj = MonthlySalary.objects.filter(user=request.user, month=current_month).first()
        current_month_salary = salary_obj.amount if salary_obj else 0
        
        # Current month expenses
        expenses = Expense.objects.filter(user=request.user, date__year=today.year, date__month=today.month)
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Remaining balance
        remaining_balance = float(current_month_salary) - float(total_expenses)
        
        # Category count
        category_count = Category.objects.filter(user=request.user).count()
        
        # Expenses by category
        expenses_by_category = []
        for cat in Category.objects.filter(user=request.user):
            cat_total = expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
            if cat_total > 0:
                expenses_by_category.append({
                    'category_name': cat.name,
                    'total': cat_total,
                    'color': cat.color
                })
                
        # Recent expenses
        recent_expenses = ExpenseSerializer(
            Expense.objects.filter(user=request.user).order_by('-date', '-created_at')[:5], 
            many=True
        ).data
        
        # Monthly trend
        monthly_trend = []
        for i in range(5, -1, -1):
            target_month = current_month - relativedelta(months=i)
            
            m_salary = MonthlySalary.objects.filter(user=request.user, month=target_month).first()
            m_salary_val = m_salary.amount if m_salary else 0
            
            m_expenses = Expense.objects.filter(user=request.user, date__year=target_month.year, date__month=target_month.month)
            m_expenses_val = m_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            
            monthly_trend.append({
                'month': target_month.strftime('%Y-%m'),
                'total_expenses': m_expenses_val,
                'salary': m_salary_val
            })
            
        return Response({
            'current_month_salary': current_month_salary,
            'total_expenses': total_expenses,
            'remaining_balance': remaining_balance,
            'category_count': category_count,
            'expenses_by_category': expenses_by_category,
            'monthly_trend': monthly_trend,
            'recent_expenses': recent_expenses
        })

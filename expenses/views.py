from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from .models import Category, MonthlyIncome, Expense, BreakdownCluster, ExpenseBreakdown
from .serializers import CategorySerializer, MonthlyIncomeSerializer, ExpenseSerializer, BreakdownClusterSerializer, ExpenseBreakdownSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MonthlyIncomeViewSet(viewsets.ModelViewSet):
    serializer_class = MonthlyIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = MonthlyIncome.objects.filter(user=self.request.user)
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

class BreakdownClusterViewSet(viewsets.ModelViewSet):
    serializer_class = BreakdownClusterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BreakdownCluster.objects.filter(
            expense_id=self.kwargs['expense_pk'],
            expense__user=self.request.user
        )

    def perform_create(self, serializer):
        expense = get_object_or_404(
            Expense, pk=self.kwargs['expense_pk'], user=self.request.user
        )
        serializer.save(expense=expense)

class ExpenseBreakdownViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseBreakdownSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExpenseBreakdown.objects.filter(
            cluster_id=self.kwargs['cluster_pk'],
            cluster__expense_id=self.kwargs['expense_pk'],
            cluster__expense__user=self.request.user
        )

    def perform_create(self, serializer):
        cluster = get_object_or_404(
            BreakdownCluster,
            pk=self.kwargs['cluster_pk'],
            expense_id=self.kwargs['expense_pk'],
            expense__user=self.request.user
        )
        serializer.save(cluster=cluster)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        current_month = today.replace(day=1)
        last_month = current_month - relativedelta(months=1)

        # ─── Opening Balance ──────────────────────────────────────────────────
        # Income for month M is credited (received) in month M+1.
        # Opening balance = all incomes credited *before* the current month
        #                 − all expenses incurred *before* the current month.
        #
        # Incomes credited before current month → income.month < current_month
        # (income.month == last_month was credited this month, so exclude it too;
        #  only incomes whose month < last_month have been credited before today's month)
        # Actually: income of month M is credited in month M+1.
        # So incomes credited BEFORE current_month means income.month < last_month.
        past_incomes_credited = MonthlyIncome.objects.filter(
            user=request.user,
            month__lt=last_month   # income.month < last_month → credited before current month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        past_expenses = Expense.objects.filter(
            user=request.user,
            date__lt=current_month  # expenses before this month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        opening_balance = float(past_incomes_credited) - float(past_expenses)

        # ─── Closing Balance ──────────────────────────────────────────────────
        # Income credited this month = sum of all last month's income records
        credited_this_month = float(
            MonthlyIncome.objects.filter(
                user=request.user, month=last_month
            ).aggregate(Sum('amount'))['amount__sum'] or 0
        )

        # Current month expenses
        expenses = Expense.objects.filter(
            user=request.user,
            date__year=today.year,
            date__month=today.month,
        )
        total_expenses = float(expenses.aggregate(Sum('amount'))['amount__sum'] or 0)

        closing_balance = opening_balance + credited_this_month - total_expenses

        # ─── Category count ───────────────────────────────────────────────────
        category_count = Category.objects.filter(user=request.user).count()

        # ─── Expenses by category (current month) ────────────────────────────
        expenses_by_category = []
        for cat in Category.objects.filter(user=request.user):
            cat_total = expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
            if cat_total > 0:
                expenses_by_category.append({
                    'category_name': cat.name,
                    'total': float(cat_total),
                    'color': cat.color
                })

        # ─── Recent expenses ──────────────────────────────────────────────────
        recent_expenses = ExpenseSerializer(
            Expense.objects.filter(user=request.user).order_by('-date', '-created_at')[:5],
            many=True
        ).data

        # ─── Monthly trend (last 6 months) ───────────────────────────────────
        monthly_trend = []
        for i in range(5, -1, -1):
            target_month = current_month - relativedelta(months=i)

            m_income_val = float(
                MonthlyIncome.objects.filter(
                    user=request.user, month=target_month
                ).aggregate(Sum('amount'))['amount__sum'] or 0
            )

            m_expenses = Expense.objects.filter(
                user=request.user,
                date__year=target_month.year,
                date__month=target_month.month,
            )
            m_expenses_val = float(m_expenses.aggregate(Sum('amount'))['amount__sum'] or 0)

            monthly_trend.append({
                'month': target_month.strftime('%Y-%m'),
                'total_expenses': m_expenses_val,
                'income': m_income_val,
            })

        return Response({
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'credited_this_month': credited_this_month,
            'total_expenses': total_expenses,
            'category_count': category_count,
            'expenses_by_category': expenses_by_category,
            'monthly_trend': monthly_trend,
            'recent_expenses': recent_expenses,
        })

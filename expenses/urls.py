from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'salary', views.MonthlySalaryViewSet, basename='salary')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
]

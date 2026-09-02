from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'income', views.MonthlyIncomeViewSet, basename='income')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
    path('expenses/<int:expense_pk>/clusters/', views.BreakdownClusterViewSet.as_view({'get': 'list', 'post': 'create'}), name='expense-clusters'),
    path('expenses/<int:expense_pk>/clusters/<int:pk>/', views.BreakdownClusterViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='expense-cluster-detail'),
    path('expenses/<int:expense_pk>/clusters/<int:cluster_pk>/items/', views.ExpenseBreakdownViewSet.as_view({'get': 'list', 'post': 'create'}), name='cluster-items'),
    path('expenses/<int:expense_pk>/clusters/<int:cluster_pk>/items/<int:pk>/', views.ExpenseBreakdownViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='cluster-item-detail'),
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
]

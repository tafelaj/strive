from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'loans_admin'

urlpatterns = [
    #path('user/create/', views.SignUpView.as_view(), name='user_create'),
    path('', views.Dash.as_view(), name='loans_admin_home'),
    #payments
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('payment/<int:pk>/detail/', views.PaymentsView.as_view(), name='payment_details'),
    #customers
    path('customers/', views.CustomerView.as_view(), name='customers'),
    path('customer/<int:pk>/loans/', views.CustomerView.as_view(), name='customer_loans'),
    #loans list
    path('loans/active/list/', views.LoansView.as_view(), name='active_loans'),
    path('loans/pending/list/', views.PendingLoansView.as_view(), name='pending_loans'),
    path('loans/completed/list/', views.CompletedLoans.as_view(), name='completed_loans'),
    #summary
    path('summary/', views.SummaryView.as_view(), name='summary'),

    #new loans
    path('loans/add/', views.IssueLoanNewCustomer.as_view(), name='new_loan_new'),
    path('loans/add/existing/', views.IssueLoanExistingCustomer.as_view(), name='new_loan_existing'),

    #stations
    path('stations/', views.StationsView.as_view(), name='stations'),

    #legal
    path('terms', views.TermsView.as_view(), name='terms')
]
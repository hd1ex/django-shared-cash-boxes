from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserOverview.as_view(), name='cash_box_index'),
    path('box/', views.CashBoxesOverview.as_view(), name='cash_box_overview'),
    path('box/<str:name>/', views.InvoiceList.as_view(),
         name='cash_box_detail_view'),
    path('box/<str:name>/transactions', views.TransactionList.as_view(),
         name='cash_box_transaction_overview'),
    path('box/<str:name>/transactions/<str:user>',
         views.TransactionList.as_view(),
         name='cash_box_transaction_user_view'),
    path('box/<str:name>/new', views.invoice_submission_view,
         name='cash_box_invoice_submission_view'),
]

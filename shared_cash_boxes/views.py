from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.translation import gettext
from django.views.generic import ListView

from shared_cash_boxes.forms import InvoiceForm
from shared_cash_boxes.models import CashBox, Euro, Invoice, Transaction


class UserOverview(LoginRequiredMixin, ListView):
    template_name = 'shared_cash_boxes/user_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_user_balance'] = CashBox.get_total_user_balance(
            self.request.user)
        context['abs_total_user_balance'] = Euro(
            abs(context['total_user_balance']))
        return context

    def get_queryset(self):
        cash_boxes = CashBox.objects.all()

        for cash_box in cash_boxes:
            cash_box.user_balance = cash_box.get_total_user_balance(
                self.request.user)

        return cash_boxes


class CashBoxesOverview(LoginRequiredMixin, ListView):
    template_name = 'shared_cash_boxes/cash_boxes_overview.html'

    def get_queryset(self):
        cash_boxes = CashBox.objects.all()

        search = self.request.GET.get('search', '')
        if search != '':
            cash_box_filter = Q(name__icontains=search)

            return cash_boxes.filter(cash_box_filter)
        else:
            return cash_boxes

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class InvoiceList(LoginRequiredMixin, ListView):
    template_name = 'shared_cash_boxes/invoice_list.html'

    def get_queryset(self):
        name = self.kwargs['name']
        invoices = Invoice.objects.filter(cash_box__name=name)

        search = self.request.GET.get('search', '')
        if search != '':
            invoice_filter = Q(description__icontains=search)

            return invoices.filter(invoice_filter)
        else:
            return invoices

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['cash_box'] = get_object_or_404(CashBox,
                                                name=self.kwargs['name'])
        context['cash_box_balance'] = context['cash_box'].get_balance()
        return context


class TransactionList(LoginRequiredMixin, ListView):
    template_name = 'shared_cash_boxes/transaction_list.html'

    def get_queryset(self):
        name = self.kwargs['name']
        transactions = Transaction.objects.filter(
            cash_box__name=name, user=self.request.user).select_subclasses()

        search = self.request.GET.get('search', '').lower()
        if search != '':
            return list(
                filter(lambda t: ((hasattr(t, 'description')
                                   and search in t.description.lower())
                                  or (not hasattr(t, 'description')
                                      and search in gettext('cash flow'))),
                       transactions.all())
            )
        else:
            return transactions

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['cash_box'] = get_object_or_404(CashBox,
                                                name=self.kwargs['name'])
        context['user_balance'] = context['cash_box'].get_user_balance(
            self.request.user)
        context['abs_user_balance'] = Euro(abs(context['user_balance']))
        return context


def invoice_submission_view(request: HttpRequest, name: str):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            invoice = Invoice(user=request.user,
                              cash_box=get_object_or_404(CashBox, name=name),
                              date=form.cleaned_data['date'],
                              amount=-form.cleaned_data['amount'] * 100,
                              description=form.cleaned_data['description'],
                              file=form.cleaned_data['file'])

            invoice.save()
            print(form.cleaned_data['file'].content_type)

            return HttpResponseRedirect(
                reverse('cash_box_detail_view', args=[name]))
    else:
        form = InvoiceForm()

    return render(request, 'shared_cash_boxes/invoice_submission.html',
                  {'form': form, 'cash_box': name})

from typing import Any, Dict, List

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse
from django.utils.translation import gettext
from django_tables2 import SingleTableView

from shared_cash_boxes.forms import InvoiceForm
from shared_cash_boxes.models import CashBox, Euro, Invoice, Transaction
from shared_cash_boxes.tables import InvoiceTable, TransactionTable, \
    DescribedTransaction, CashBoxTable, UserOverviewTable


class UserOverview(LoginRequiredMixin, SingleTableView):
    template_name = 'shared_cash_boxes/user_overview.html'
    table_class = UserOverviewTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_user_balance'] = CashBox.get_total_user_balance(
            self.request.user)
        context['abs_total_user_balance'] = Euro(
            abs(context['total_user_balance']))
        context['table'] = UserOverviewTable(self.get_queryset(),
                                             request=self.request)
        return context

    def get_queryset(self):
        # Return all users, which are active or have debts
        users: List[User] = []

        for user in User.objects.all():
            if user.is_active or CashBox.get_total_user_balance(user) != 0:
                users.append(user)

        return users


class CashBoxesOverview(LoginRequiredMixin, SingleTableView):
    template_name = 'shared_cash_boxes/cash_boxes_overview.html'
    table_class = CashBoxTable

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
        context['table'] = CashBoxTable(self.get_queryset(),
                                        request=self.request)
        return context


class InvoiceList(LoginRequiredMixin, SingleTableView):
    template_name = 'shared_cash_boxes/invoice_list.html'
    table_class = InvoiceTable

    def get_queryset(self):
        name = self.kwargs['name']
        cash_box = get_object_or_404(CashBox, name=name)
        invoices = Invoice.objects.filter(cash_box=cash_box)

        search = self.request.GET.get('search', '')
        if search != '':
            invoice_filter = Q(description__icontains=search)

            res = list(invoices.filter(invoice_filter).all())
        else:
            res = list(invoices.all())

        if cash_box.initial_amount != 0:
            res.append(Invoice(description=gettext('Initial amount'),
                               amount=cash_box.initial_amount,
                               cash_box=cash_box,
                               date=None))
        return res

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['cash_box'] = get_object_or_404(CashBox,
                                                name=self.kwargs['name'])
        context['cash_box_balance'] = context['cash_box'].get_balance()
        context['table'] = InvoiceTable(self.get_queryset(),
                                        request=self.request,
                                        order_by="-date")
        return context


class TransactionList(LoginRequiredMixin, SingleTableView):
    template_name = 'shared_cash_boxes/transaction_list.html'
    table_class = TransactionTable

    def get_user_from_kwargs(self):
        username = self.kwargs.get('user')
        if username is None:
            return self.request.user
        else:
            return get_object_or_404(User, username=username)

    def get_queryset(self):
        name = self.kwargs['name']
        user = self.get_user_from_kwargs()

        transactions = [DescribedTransaction(**vars(t)) for t in
                        Transaction.objects.filter(
                            cash_box__name=name,
                            user=user).select_subclasses().all()]

        search = self.request.GET.get('search', '').lower()
        if search != '':
            return list(filter(lambda t: search in t.description.lower(),
                               transactions))
        else:
            return transactions

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.get_user_from_kwargs()
        context['user'] = user.get_full_name()
        context['search'] = self.request.GET.get('search', '')
        context['cash_box'] = get_object_or_404(CashBox,
                                                name=self.kwargs['name'])
        context['user_balance'] = context['cash_box'].get_user_balance(user)
        context['abs_user_balance'] = Euro(abs(context['user_balance']))
        context['table'] = TransactionTable(self.get_queryset(),
                                            request=self.request,
                                            order_by="-date")
        return context


@login_required
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

            return HttpResponseRedirect(
                reverse('cash_box_detail_view', args=[name]))
    else:
        form = InvoiceForm()

    return render(request, 'shared_cash_boxes/invoice_submission.html',
                  {'form': form, 'cash_box': name})

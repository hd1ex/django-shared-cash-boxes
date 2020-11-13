from collections import OrderedDict
from typing import List

import django_tables2 as tables
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext

from .models import Invoice, Euro, CashBox


class EuroColumn(tables.Column):
    def render(self, value):
        return Euro(value)


class FileColumn(tables.Column):
    def render(self, value):
        return format_html('<a href="/files/{}">'
                           + gettext('Invoice') +
                           '</a>', value)


class UserColumn(tables.Column):
    def render(self, value):
        return value.get_full_name()


class CashBoxBalanceRow:
    def __init__(self, name: str, balance: Euro):
        self.name = name
        self.balance = balance


class DescribedTransaction:
    def __init__(self, **kwargs):
        self.date = kwargs.get('date')
        self.amount = kwargs.get('amount')
        self.user = kwargs.get('user')
        self.description = kwargs.get('description', gettext('Cash flow'))


class UserBalance:
    def __init__(self, cash_box: CashBox, user: User):
        self.cash_box = cash_box
        self.user = user
        self.amount = cash_box.get_user_balance(user)

    def __eq__(self, other):
        return hasattr(other, 'amount') and self.amount == other.amount

    def __ne__(self, other):
        return hasattr(other, 'amount') and self.amount != other.amount

    def __lt__(self, other):
        return self.amount < other.amount

    def __le__(self, other):
        return self.amount <= other.amount

    def __gt__(self, other):
        return self.amount > other.amount

    def __ge__(self, other):
        return self.amount >= other.amount

    def __str__(self):
        return str(self.amount)


class UserBalanceColumn(tables.Column):
    def render(self, value: UserBalance):
        return format_html(
            '<a href ="{}">{}</a>',
            reverse('cash_box_transaction_user_view',
                    kwargs={'name': value.cash_box.name,
                            'user': value.user.username}),
            value.amount)


class UserOverviewTable(tables.Table):
    user = UserColumn()

    def __init__(self, data, *args, **kwargs):
        users: List[User] = data
        cash_boxes: QuerySet[CashBox] = CashBox.objects.all()
        extra_columns = {}
        rows = OrderedDict()

        for cash_box in cash_boxes:
            extra_columns[cash_box.name] = UserBalanceColumn()

        for user in users:
            rows[user.id] = {'user': user}

            for cash_box in cash_boxes:
                rows[user.id][cash_box.name] = UserBalance(cash_box, user)

        super().__init__(data=rows.values(),
                         extra_columns=extra_columns.items(),
                         *args, **kwargs)

    def render_name(self, value):
        return format_html(
            '<a href ="{}">{}</a>',
            reverse('cash_box_transaction_overview', kwargs={'name': value}),
            value)

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-striped'}


class CashBoxTable(tables.Table):
    current_balance = EuroColumn(orderable=False)

    def render_name(self, value):
        return format_html(
            '<a href ="{}">{}</a>',
            reverse('cash_box_detail_view', kwargs={'name': value}),
            value)

    class Meta:
        model = CashBox
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-striped'}
        fields = ('name', 'current_balance',)


class InvoiceTable(tables.Table):
    amount = EuroColumn()
    file = FileColumn()
    user = UserColumn()
    date = tables.DateColumn(settings.DATE_FORMAT)

    class Meta:
        model = Invoice
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-striped'}
        fields = ('date', 'description', 'user', 'file', 'amount',)


class TransactionTable(tables.Table):
    date = tables.DateColumn(settings.DATE_FORMAT)
    description = tables.Column()
    amount = EuroColumn()

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-striped'}
        fields = ('date', 'description', 'amount',)

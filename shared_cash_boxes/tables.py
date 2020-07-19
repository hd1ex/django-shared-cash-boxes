import django_tables2 as tables
from django.conf import settings
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


class UserOverviewTable(tables.Table):
    user_balance = EuroColumn(orderable=False)

    def render_name(self, value):
        return format_html(
            '<a href ="{}">{}</a>',
            reverse('cash_box_transaction_overview', kwargs={'name': value}),
            value)

    class Meta:
        model = CashBox
        template_name = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-striped'}
        fields = ('name', 'user_balance',)


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

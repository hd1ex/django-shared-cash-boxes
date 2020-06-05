import datetime
from gettext import gettext

from django import forms


class InvoiceForm(forms.Form):
    description = forms.CharField(
        label=gettext('Invoice description')
    )
    date = forms.DateField(
        label=gettext('Date of payment'),
        widget=forms.TextInput(
            attrs={'type': 'date'}
        ),
        initial=datetime.date.today
    )
    amount = forms.DecimalField(
        label=gettext('Amount you paid in Euro'),
        decimal_places=2,
    )
    file = forms.FileField(
        label=gettext('The invoice as pdf/image file'),
        help_text=gettext(
            'Make a photo if the invoice is not available digitally. '
            'Also save the invoice, especially if a product has warranty.'),
    )

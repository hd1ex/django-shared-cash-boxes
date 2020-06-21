import datetime
import fnmatch
import os
import pathlib
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext
from model_utils.managers import InheritanceManager


def get_unique_invoice_filename(instance, filename: str) -> pathlib.Path:
    date = datetime.date.today().isoformat()
    ext = os.path.splitext(filename)[1]
    assert settings.MEDIA_ROOT, 'Please set MEDIA_ROOT for user uploaded files'
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    media = os.listdir(settings.MEDIA_ROOT)
    num = 1

    while True:
        name = f'invoice-{date}-{num}'

        if len(fnmatch.filter(media, f'{name}*')) == 0:
            return pathlib.Path(f'{name}{ext}')
        num += 1


class Euro(int):
    def __new__(cls, cent: int, *args, **kwargs):
        return super().__new__(cls, cent)

    def __str__(self) -> str:
        return f"{self / 100} €"


class CashBox(models.Model):
    """A cash box"""
    name = models.TextField(help_text=gettext('The name of the cash box.'),
                            unique=True)
    initial_amount = models.IntegerField(
        help_text=gettext('The initial value of the cash box.'), default=0)

    def __str__(self):
        return self.name

    def get_balance(self, date: Optional[datetime.date] = None) -> Euro:
        """
        Returns the amount of money that should (theoretically) be in the cash
         box after every asset is paid
        :param date is an optional billed until
        """
        cash = self.initial_amount

        for transaction in self.transaction_set.select_subclasses().all():
            if date is None or transaction.date <= date:
                if isinstance(transaction, Invoice):
                    cash += transaction.amount

        return Euro(cash)

    def get_user_balance(self, user: User,
                         date: Optional[datetime.date] = None) -> Euro:
        """
        Returns the amount of money that the user owes or lends the cash box
        :param user is the user to calculate for
        :param date is an optional billed until
        """
        cash = 0

        for transaction in self.transaction_set.select_subclasses().filter(
                user=user).all():
            if date is None or transaction.date <= date:
                cash -= transaction.amount

        return Euro(cash)

    @staticmethod
    def get_total_user_balance(user: User,
                               date: Optional[datetime.date] = None) -> Euro:
        """
        Returns the amount of money that the user owes or lends all cash boxes
        :param user is the user to calculate for
        :param date is an optional billed until
        """
        cash = 0

        for cash_box in CashBox.objects.all():
            cash += cash_box.get_user_balance(user, date)

        return Euro(cash)


class Transaction(models.Model):
    user = models.ForeignKey(User, help_text=gettext(
        'The user this transaction applies to.'), on_delete=models.CASCADE)
    cash_box = models.ForeignKey(CashBox,
                                 help_text=gettext('The cash box to balance.'),
                                 on_delete=models.CASCADE)
    date = models.DateField(help_text=gettext('The date of the payment.'),
                            default=datetime.date.today)
    amount = models.IntegerField(
        help_text=gettext('The amount of the transaction.'))

    objects = InheritanceManager()

    def __str__(self):
        return gettext(
            f'{self.get_amount()} from {self.cash_box} to {self.user}')

    def get_amount(self) -> Euro:
        return Euro(self.amount)


class Invoice(Transaction):
    """This describes an invoice that is already paid by an user
     which has to be balanced by the cash box"""

    description = models.TextField(
        help_text=gettext('A short description of the invoice.'))
    file = models.FileField(
        help_text=gettext('A pdf or image of the invoice.'),
        upload_to=get_unique_invoice_filename,
        null=True, blank=True)

    def __str__(self):
        return self.description

# Generated by Django 3.0.6 on 2020-05-24 22:01

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import shared_cash_boxes.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CashBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name',
                 models.TextField(help_text='The name of the cash box.',
                                  unique=True)),
                ('initial_amount',
                 models.IntegerField(default=0,
                                     help_text='The initial value of the cash box.')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today,
                                          help_text='The date of the payment.')),
                ('amount', models.IntegerField(
                    help_text='The amount of the transaction.')),
                ('cash_box',
                 models.ForeignKey(help_text='The cash box to balance.',
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='shared_cash_boxes.CashBox')),
                ('user', models.ForeignKey(
                    help_text='The user this transaction applies to.',
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('transaction_ptr',
                 models.OneToOneField(auto_created=True,
                                      on_delete=django.db.models.deletion.CASCADE,
                                      parent_link=True,
                                      primary_key=True,
                                      serialize=False,
                                      to='shared_cash_boxes.Transaction')),
                ('description', models.TextField(
                    help_text='A short description of the invoice.')),
                ('file',
                 models.FileField(blank=True,
                                  help_text='A pdf or image of the invoice.',
                                  null=True,
                                  upload_to=shared_cash_boxes.models.get_unique_invoice_filename)),
            ],
            bases=('shared_cash_boxes.transaction',),
        ),
    ]

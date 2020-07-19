=================
Shared Cash Boxes
=================

Shared Cash Boxes is a Django app to manage, well, shared cash boxes.

The general cash box balance is tracked with invoices.

The balance with users is tracked with transactions described as
*cash flow*. An invoice therefore 'unbalances' an users account
and a cash flow can balance this again.
To be quit with the system, a user should have a balance of 0.

The treasurer should be a Django admin.

Quick start
-----------

1. Add "shared_cash_boxes" and its dependencies "django_bootstrap_breadcrumbs",
"django_tables2" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_bootstrap_breadcrumbs',
        'django_tables2',
        'shared_cash_boxes',
    ]

2. Include the shared_cash_boxes URLconf in your project urls.py like this::

    path('shared_cash_boxes/', include('shared_cash_boxes.urls')),

3. Run ``python manage.py migrate`` to create the shared cash boxes models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a cash box and other data (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/cash/ to view the data as a normal user.


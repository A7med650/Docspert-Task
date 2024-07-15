from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction

from .models import Account
from .forms import AccountTransferForm

import pandas as pd

import uuid

# Create your views here.


def upload_accounts(request):
    if request.method=='POST':
        file = request.FILES['file']

        # Check File Type to end with .csv, .xls, or .xlsx
        if not file.name.endswith(('.csv', '.xls', '.xlsx')):
            messages.error(request, 'Invalid file type. Please upload a CSV or Excel file.')
            return render(request, 'index.html')
        
        # Read File
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            existing_ids = [str(o) for o in Account.objects.values_list('id', flat=True)]
            new_accounts = df[~df['ID'].isin(existing_ids)]
            data_entry = []
            for _,row in new_accounts.iterrows():
                data_entry.append(Account(id=row['ID'], name=row['Name'], balance=row['Balance']))
            Account.objects.bulk_create(data_entry)

            messages.success(request, f'{len(data_entry)} rows imported successfully.')

        except Exception as ex:
            messages.error(request, f'Error importing accounts: {str(ex)}')
    return render(request, "index.html")

def account_list(request):
    accounts = Account.objects.all().order_by('name')

    paginator = Paginator(accounts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "accounts":page_obj,
    }
    return render(request,'accounts.html', context)

def account_detail(request, pk):
    try:
        uuid_id = uuid.UUID(pk, version=4)
    except:
        raise Http404("Please Enter Valid UUID")
    account = get_object_or_404(Account, id=pk)

    context = {
        "account":account,
    }
    return render(request, "account_detail.html", context)

def transfer(request):
    form = AccountTransferForm()
    context = {
        'form': form,
    }
    if request.method == 'POST':
        form = AccountTransferForm(request.POST)
        if form.is_valid():
            source_account = form.cleaned_data['source_account']
            target_account = form.cleaned_data['target_account']
            amount = form.cleaned_data['amount']

            two_accounts = Account.objects.filter(name__in=[source_account, target_account])

            if len(two_accounts)!=2 or two_accounts[0]==two_accounts[1]:
                messages.error(request, "You cannot transfer amount to the same user")
                return render(request, "transfer.html", context)
            source = two_accounts[0]
            target = two_accounts[1]

            if amount<=0:
                messages.error(request, "The amount must be greater than zero.")
                return render(request, "transfer.html", context)
            
            if source.balance<amount:
                messages.error(request, f"Insufficient balance {source.name} doesn't have this value {amount}!")
                return render(request, "transfer.html", context)
            
            try:
                with transaction.atomic():
                    source.balance -= amount
                    target.balance += amount
                    source.save()
                    target.save()
                    transaction.on_commit(lambda: messages.success(
                            request, f'Transfer successful from {source.name} to {target.name} and the amount was {amount}'))
            except:
                messages.error(request, 'Transfer Failed due to something wrong!')
                return render(request, "transfer.html", context)

    return render(request,'transfer.html', context)


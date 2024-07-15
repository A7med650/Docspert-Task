from django import forms

from .models import Account

class AccountTransferForm(forms.Form):
    source_account = forms.ModelChoiceField(
        queryset=Account.objects.only('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Source Account",
        label_suffix="")
    
    target_account = forms.ModelChoiceField(
        queryset=Account.objects.only('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Targe Account",
        label_suffix="")
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Amount",
        label_suffix="")
from django.test import TestCase
from django.urls import reverse
from .models import Account

import uuid
from io import StringIO

# Create your tests here.


class AccountTestCase(TestCase):
    def setUp(self):
        self.account1 = Account.objects.bulk_create(
            [
                Account(uuid.uuid4(), "Ahmed Mostafa", 1500.00),
                Account(uuid.uuid4(), "Ahmed Fouda", 500.00),
            ]
        )
    
    def test_import_accounts(self):
        csv_data = StringIO('ID,Name,Balance\n16fd2706-8baf-433b-82eb-8c7fada847da,Menna Mohamed,3000.00\n25fa2706-8baf-433b-82eb-8c7fada047da,Amgad Mohasen,300.00\n')
        csv_data.name = 'test.csv'
        response = self.client.post(reverse('upload_accounts'), {'file': csv_data}, format='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Account.objects.count(), 4)

    def test_account_list(self):
        response = self.client.get(reverse('accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.account1[0].name)
        self.assertContains(response, self.account1[1].name)

    def test_account_detail(self):
        response = self.client.get(reverse('account_detail', args=[self.account1[0].pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.account1[0].name)
        self.assertContains(response, self.account1[0].balance)
    
    def test_transfer_valid(self):
        transfer_data = {
            'source_account': self.account1[0].id,
            'target_account': self.account1[1].id,
            'amount': 500.00
        }
        response = self.client.post(reverse('transfer'), data=transfer_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Account.objects.get(name=self.account1[0].name).balance, 1000.00)
        self.assertEqual(Account.objects.get(name=self.account1[1].name).balance, 1000.00)
    
    def test_transfer_insufficient(self):
        transfer_data = {
            'source_account': self.account1[0].id,
            'target_account': self.account1[1].id,
            'amount': 2000.00
        }

        response = self.client.post(reverse('transfer'), transfer_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer.html')
        msgs = [msg for msg in response.context['messages']]
        self.assertEqual(len(msgs), 1)
    
    def test_transfer_same_user(self):
        transfer_data = {
            'source_account': self.account1[0].id,
            'target_account': self.account1[0].id,
            'amount': 500.00
        }

        response = self.client.post(reverse('transfer'), transfer_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transfer.html')
        msgs = [msg for msg in response.context['messages']]
        self.assertEqual(len(msgs), 1)

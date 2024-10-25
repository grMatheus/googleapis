from __future__ import print_function
from http import server
from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import os.path
import re
import sys
import getopt
import requests

# If modifying these scopes, delete the file token.json.
MATTERID = '97b226fd-432e-4463-831b-a1c63e81b68d'
SCOPES = ['https://www.googleapis.com/auth/ediscovery', 'https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.user.readonly', 'https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = r'C:\Users\matheus.guerreiro\google_apis\credentials.json'
EMAIL = 'matheus.guerreiro@kabum.com.br'

def main():
    return

def build_service_directory_admin():
     creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=EMAIL)
     
     service = build('admin', 'directory_v1', credentials=creds)
     return service

def build_service_vault_api():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=EMAIL)

    service = build('vault', 'v1', credentials=creds)
    return service


def list_suspended_users(service):
	results = service.users().list(customer='my_customer', maxResults=20,orderBy='email', query='isSuspended=true').execute()
	users = results.get('users', [])
	sus_users = []
	for user in users:
		sus_users.append(user['primaryEmail'])
	print('Usuarios suspensos: ')
	print(sus_users)
	return sus_users

def list_exports(service, matter_id):
	results = service.matters().exports().list(matterId=matter_id).execute()
	exports = results.get('exports', [])
	existent_exports = []
	for export in exports:
		existent_exports.append(export['name'])
	print('Backups exportados: ')
	print(existent_exports)
	return existent_exports

def compare(sus_users, exports):
	users_to_export = []
	for user in sus_users:
		if user not in exports:
			users_to_export.append(user)
	print('Contas pendentes de exportacao: ')
	print(users_to_export)
	return users_to_export

def create_mailbox_export(service, matter_id, users):
    emails_to_search = users
    mail_query_options = {'excludeDrafts': True}
    matter_Id = '97b226fd-432e-4463-831b-a1c63e81b68d'
    #query_terms = args.gmail_account
    mail_query = {
        'corpus': 'MAIL',
        'dataScope': 'ALL_DATA',
        'searchMethod': 'ACCOUNT',
        'accountInfo': {
            'emails': emails_to_search
        },
        #'terms': query_terms,
        'mailOptions': mail_query_options,
    }
    mail_export_options = {
        'exportFormat': 'PST',
        'showConfidentialModeContent': True
    }
    wanted_export = {
        'name': users,
        'query': mail_query,
        'exportOptions': {
        'mailOptions': mail_export_options
        }
    }
    return service.matters().exports().create(matterId=matter_Id, body=wanted_export).execute()

#Call main
if __name__ == '__main__':
    directoryService = build_service_directory_admin()
    vaultService = build_service_vault_api()
    #list_suspended_users(directoryService)
    suspended_users = list_suspended_users(directoryService)
    matter_id = MATTERID
    exports = list_exports(vaultService, matter_id)
    pendent_export = compare(suspended_users, exports)
    for user in pendent_export:
    	create_mailbox_export(vaultService, matter_id, user)
from __future__ import print_function
from http import server
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.cloud import storage
import os.path
import re
import sys
import getopt
import requests
from tqdm import tqdm

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/ediscovery', 'https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.user.readonly', 'https://www.googleapis.com/auth/cloud-platform']

# Set environment variables
os.environ['MATTERID'] = '97b226fd-432e-4463-831b-a1c63e81b68d'

SERVICE_ACCOUNT_FILE = r'C:\Users\matheus.guerreiro\Desktop\google_backup\credentials.json'
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
	results = service.users().list(customer='my_customer', maxResults=5,orderBy='email', query='isSuspended=true').execute()
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

def download_exports(service, matter_id):

    gcpClient = storage.Client()
    matter_id = os.environ['MATTERID']
    for export in vaultService.matters().exports().list(
          matterId=matter_id).execute()['exports']:
        if 'cloudStorageSink' in export:
          directory = export['name']
          if not os.path.exists(directory):
            os.makedirs(directory)
          print(export['id'])
          for sinkFile in export['cloudStorageSink']['files']:
            filename = '%s/%s' % (directory, sinkFile['objectName'].split('/')[-1])
            objectURI = 'gs://%s/%s' % (sinkFile['bucketName'],
                                        sinkFile['objectName'])
            filesize = (sinkFile['size'])
            print('get %s to %s %s' % (objectURI, filename, filesize))
            with open(filename, 'wb') as f:
                with tqdm(total=int(filesize), desc="Downloading", initial=0, unit_scale=True) as pbar:
                    gcpClient.download_blob_to_file(objectURI, open(filename, 'wb+'))
                    for size in filesize:
                        pbar.update()
                    pbar.close()


#Call main
if __name__ == '__main__':
    directoryService = build_service_directory_admin()
    vaultService = build_service_vault_api()
    #list_suspended_users(directoryService)
    suspended_users = list_suspended_users(directoryService)
    matter_id = '97b226fd-432e-4463-831b-a1c63e81b68d'
    exports = list_exports(vaultService, matter_id)
    pendent_export = compare(suspended_users, exports)
    download_exports(vaultService, matter_id)

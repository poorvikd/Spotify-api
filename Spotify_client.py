#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import base64
import requests
import datetime
from urllib.parse import urlencode


# In[ ]:


class SpotifyAPI(object):
    access_token=None
    access_token_expires=datetime.datetime.now()
    access_token_did_expire=True
    client_id=None
    client_secret=None
    token_url='https://accounts.spotify.com/api/token'
    def __init__(self,client_id,client_secret,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.client_id=client_id
        self.client_secret=client_secret
    def get_client_credentials(self):
        client_id=self.client_id
        client_secret=self.client_secret
        if client_secret==None or client_id==None:
            raise Exception("You must have a client_id and client_secret")
        client_creds=f"{client_id}:{client_secret}"
        client_creds_b64=base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    def get_token_header(self):
        client_creds_b64=self.get_client_credentials()
        return {'Authorization':f"Basic {client_creds_b64}"}
    def get_token_data(self):
        return {'grant_type':'client_credentials'}
    def perform_auth(self):
        token_url=self.token_url
        token_data=self.get_token_data()
        token_header=self.get_token_header()
        r=requests.post(token_url,data=token_data,headers=token_header)
        if r.status_code not in range(200,299):
            return False
        data=r.json()
        now=datetime.datetime.now()
        access_token=data['access_token']
        self.access_token=access_token
        expires_in=data['expires_in']
        expires=now+datetime.timedelta(seconds=expires_in)
        self.access_token_expires=expires
        self.access_token_did_expire=now<expires
        return True
    def get_access_token(self):
        token=self.access_token
        expires=self.access_token_expires
        now=datetime.datetime.now()
        if expires<now:
            self.perform_auth()
            return self.get_access_token()
        elif token==None:
            self.perform_auth()
            return self.get_access_token()
        return token
    def resource_headers(self):
        access_token=self.get_access_token()
        header={'Authorization':f"Bearer {access_token}"}
        return header
    
    def base_search(self,query_params):
        header=self.resource_headers()
        endpoint='https://api.spotify.com/v1/search'
        data=query_params
        url=f'{endpoint}?{data}'
        r=requests.get(url,headers=header)
        if r.status_code in range(200,299):
            return r.json()
        return {}
    def search(self,query=None,search_type='artist',operator=None,operator_query=None):
        if query==None:
            raise Exception("No Query Passed.")
        if isinstance(query,dict):
            query=" ".join([f'{k}:{v}'for k,v in query.items()])
        if operator!=None and operator_query!=None:
            if operator.lower()=='or' or operator.lower()=='not':
                operator=operator.upper()
                if isinstance(operator,str):
                    query=f'{query} {operator} {operator_query}'
        query_params=urlencode({'q':query,'type':search_type.lower()})
        return self.base_search(query_params)
    
    def get_album(self,album_id):
        endpoint=f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        header=self.resource_headers()
        r=requests.get(endpoint,headers=header)
        if r.status_code not in range(200,299):
            raise Exception('Check url')
        return r.json()
    def get_artist(self,artist_id):
        endpoint=f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks'
        header=self.resource_header()
        data=urlencode({'country':'IN'})
        url=f'{endpoint}?{data}'
        r=requests.get(url,headers=header)
        if r.status_code not in range(200,299):
            raise Exception('Check url')
        return r.json()
        


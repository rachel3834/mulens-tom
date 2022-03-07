# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 22:44:22 2017

@author: rstreet
"""
from sys import argv
from os import path
import requests

LCO_API_URL = 'https://lco.global/observe/api/'

def get_api_token(config):
    url = path.join(LCO_API_URL,'api-token-auth/')
    params = {'username': config['user_id'], 'password': config['odin_access']}
    print url, params
    response = requests.post(url,data=params).json()
    print response
    
    token = response.get('token')
    return token

if __name__ == '__main__':
    
    user_id = raw_input('Please enter your username: ')
    pswd = raw_input('Please enter your password: ')    
    config = {'user_id': user_id, 'odin_access': pswd}
    token = get_api_token(config)
    print token
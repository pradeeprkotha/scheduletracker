# importing the requests library 
import re
import os
import sys 
import json
import logging
import boto3
import pymysql
import requests
import time
from log import Log

class SaveInfo(object):
    
    def __init__(self, env):
        self.env = env
        self.api_version = '1.0.0'
        self.logger = logging.getLogger()
        self.logger.setLevel(self.env['LOGLEVEL'])
        self.API_ENDPOINT = self.env['Schedule_API_ENDPOINT']
        self.API_KEY = self.env['Schedule_API_KEY']
        self.url = self.env['AWS_base_url']
        
        try:
            self.con = pymysql.connect(self.env['RDS_HOST'], self.env['RDS_USERNAME'], self.env['RDS_PASSWORD'],
                                       self.env['RDS_DATABASE'])
        except ClientError as e:
            self.logger.error("Database Connection ERROR: " + str(e))
            return {"version": self.api_version, "message": "failed", "statusCode": 500,
                    "error": "Unable to connect Database"}
        self.cursor = self.con.cursor(pymysql.cursors.DictCursor)
	# Save user inputs to database
    
    
   
                    
       
def lambda_handler(event,context):
    print(event)
    if event['context']['http-method'] == 'POST':
        job_id = event['body-json']['job_id']
        if 'method' in event['body-json']:
            emails_to_send = ''
        elif 'error' in event['body-json']:
            error_info =event['body-json']['error']
        else:
            users = event['body-json']['users']
            Schedule_url =  event['body-json']['Schedule_url']
            company = event['body-json']['company']
            filename = event['body-json']['filename']
    else :
        return {
            'code': 400,
            'status': 'error',
            'data': 'something went wrong'
        }   
    alias = context.invoked_function_arn.split(':')[-1]
    if alias == context.function_name:
        alias = 'DEV'
   

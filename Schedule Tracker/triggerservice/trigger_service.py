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

class MailTrigger(object):
    
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
    
    def send_mail(self,job_id,emails_to_send,_url,company,filename):
        print('Started mail sending ...')
        self.logger.info("MailTrigger event job_id and emails_to_send" + str(job_id) + str(emails_to_send))
        
        if str(emails_to_send) != "":
            SENDER = str(self.env['APP_NAME'])+" <"+str(self.env['FROM_NAME'])+">"
            print('SENDER :' + SENDER)
            AWS_REGION = self.env['REGION']
            SUBJECT = str(company) +": Schedule Job Ready to process - "+ str(job_id)    
            print('SUBJECT :' + SUBJECT)
            self.cursor.execute("SELECT  where jb.id= %s", str(job_id)) 
            job_details = self.cursor.fetchone()
            print(f'job_details :{job_details}')
            self.cursor.execute("SELECT emails FROM customers where date in (%s)", str(job_details['date_range'])) 
            primary_lang = self.cursor.fetchone()
            print(f'primary_lang :{primary_lang}')
            CUSTOM_BODY_HTML = """<body style="padding: 0;margin: 0;font-family: 'Raleway', sans-serif;height:100%;background:#dddddd14;">
                               # Body to send email
                                </body>"""
            CHARSET = "UTF-8"
            client = boto3.client('ses',region_name=AWS_REGION)
            # emails_to_send = self.env['ALERT_TO_MAIL_IDS'].split(',')
            print('mail alerts...')
            self.logger.info("mail alerts")     
            emails_to_send =emails_to_send.split(',')
            for email in emails_to_send:
                try:
                    response = client.send_email(
                        Destination={
                            'ToAddresses': [
                                email,
                            ],
                        },
                        Message={
                            'Body': {
                                'Html': {
                                    'Charset': CHARSET,
                                    'Data': CUSTOM_BODY_HTML,
                                }
                            },
                            'Subject': {
                                'Charset': CHARSET,
                                'Data': SUBJECT,
                            },
                        },
                        Source=SENDER
                    )                    
                # Display an error if something goes wrong.	
                except Exception as e:
                    self.logger.error("Unable to send email: %s" % str(e))
                else:
                    self.logger.info("Email sent! Message ID: %s" % str(response['MessageId']))
        self.con.commit()
        self.con.close()
        print('end MailTrigger...')
        
        return 'Successfully sent emails'
   
                    
       
def lambda_handler(event,context):
    print(event)
    if event['context']['http-method'] == 'POST':
        job_id = event['body-json']['job_id']
        if 'method' in event['body-json']:
            emails_to_send = ''
        elif 'error' in event['body-json']:
            error_info =event['body-json']['error']
        else:
            emails_to_send = event['body-json']['emails_to_send']
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
   

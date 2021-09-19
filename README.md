# scheduletracker
Add and remove services 
Send Scheduled emails


1. API endpoint to receive the customer products information
2. Schedule service lambda function to get data from APIgateway endpoint and save data into aurora serverless
3. Cloudwatch rule (its just like a cronjob) it will trigger mail trigger service everyday to get the products which are expiring in near future
4. Mail trigger lambda function will check the date range and pick up the email ids of the customers and trigger emails via SES service.

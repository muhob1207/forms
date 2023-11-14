from flask import Flask, request
from pymongo import MongoClient
import os
import re

app = Flask(__name__)

# Getting the MongoDB related enviormental variables
mongo_username = os.environ.get('MONGO_DB_USERNAME')
mongo_password = os.environ.get('MONGO_DB_PASSWORD')
mongo_host = os.environ.get('MONGO_DB_HOST')
mongo_port = os.environ.get('MONGO_DB_PORT')

# Establishing connection with MongoDB
mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}"

# Creating the MongoDB client
client = MongoClient(mongo_uri)

#This function checks if the phone has a correct format
#Correct format is +7 and 10 numbers +7
def is_valid_phone(phone_number):
    pattern = re.compile(r'^\+7\d{10}$')
    match = pattern.match(phone_number)

    if match:
        return True
    else:
        return False

#This function checks if the date has a correct format
#Correct format is DD.MM.YYYY or YYYY-MM-DD
#We also check that the month is less than or equal to 12 | day is less than or equal to 31
def is_valid_date(date):
    date_pattern1 = r'^\d{2}\.\d{2}\.\d{4}$'
    date_pattern2 = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern1, date):
        split_date = date.split('.')
        day = int(split_date[0])
        month = int(split_date[1])
        year = int(split_date[2])
        
        if month <= 12 and day <= 31:
            return True
        else:
            return False
    elif re.match(date_pattern2, date):
        split_date = date.split('-')
        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])
        
        if month <= 12 and day <= 31:
            return True
        else:
            return False
    else:
        return False

#Checking if the email is in correct format
#Correct format is example@example.com
def is_valid_email(text):
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    match = email_pattern.match(text)
    return bool(match)

#Creating the get_form endpoint that accepts post requests
@app.route('/get_form', methods=['POST'])
def insert_data():
    #Getting the request data
    #We are expecting that the the request data looks like:
    '''
    data = {
    'first_name': 'Ivan',
    'last_name': 'Ivanov',
    'phone': '+71234567891',
    'email': 'example@example.com',
    'birth_date': '31.07.2009'
    }
    '''
    request_data = request.get_json()
    #Connecting to the 'forms' database
    db = client.forms  
    #Connecting to the 'templates' collection
    collection = db.templates  
    #Getting all documents inside the templates collection
    templates = collection.find()

    result = None

    #Template looks like this:
    '''
    {
    _id: ObjectId('6553842447c5ded672316d1b'),
    name: 'CustomerForm',
    first_name: 'text',
    last_name: 'text',
    phone: 'phone',
    email: 'email',
    birth_date: 'date'
    }
    '''

    #Looping through all templates
    for template in templates:

        #Declaring all_fields_valid variable. If this variable is True at the end of the cycle then the template and all kets inside it are valid
        #'valid' means that all keys inside the document except '_id' and 'name' are also keys of request_data and the data types of key values inside request_data correspond
        #to the data types of the same keys inside template
        all_fields_valid = False

        template_fields = template.copy()
        template_fields.pop('_id')
        template_fields.pop('name')

        #Looping through all keys inside the template
        for template_field_name, template_field_type in template_fields.items():
            #Looping through all keys inside request_data
            for request_field_name, request_field_value in request_data.items():
                
                #For a certain key inside a template if a key with the same name is found inside request_data
                if request_field_name == template_field_name:
                    #and if the data type of the key inside the request_data is equal to the data type of the key inside the template
                    #then we say that the match for the current template key inside the request_data has been found
                    #so we break and move to the next template key
                    #else, we continue looking for a match

                    if template_field_type == 'date':
                        if is_valid_date(request_field_value):
                            all_fields_valid = True
                            break
                        else:
                            all_fields_valid = False
                    elif template_field_type == 'phone':
                        if is_valid_phone(request_field_value):
                            all_fields_valid = True
                            break
                        else:
                            all_fields_valid = False
                    elif template_field_type == 'email':
                        if is_valid_email(request_field_value):
                            all_fields_valid = True
                            break
                        else:
                            all_fields_valid = False
                    else:
                        all_fields_valid = True
                        break

                else:
                    all_fields_valid = False
            
            #If we finished looping through request_data and did not find a match then all_fields_valid remains False, so we stop looping
            #through other keys of this template as this has no point as the template is already invalid
            if all_fields_valid == False:
                break
        
        #If The loop through all parameters of the template has finished and all_fields_valid remained valid, then we found matches for all
        #keys inside this template and therefore this template is valid
        #so we founf the correct template and so we will return its name
        if all_fields_valid == True:
            result = template['name']
            break
    
    #If the correct template has not been found
    if not result:
        result = {}
        #Then we loop through all keys inside the request_data and determine their data types to form a dictionary that shows the data type
        #of each of those keys and return it in the response
        for request_field_name, request_field_value in request_data.items():

            if is_valid_date(request_field_value):
                result[request_field_name] = 'date'
            elif is_valid_phone(request_field_value):
                result[request_field_name] = 'phone'
            elif is_valid_email(request_field_value):
                result[request_field_name] = 'email'
            else:
                result[request_field_name] = 'text'
    
    return result



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

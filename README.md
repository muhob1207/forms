# Instructions

1)Clone this repository using $ git clone https://github.com/muhob1207/forms

2)In terminal navigate into the forms directory inside the forms repository that you cloned. In other words run twice $ cd forms

3)You should be inside the directory which has docker-compose.yml inside it. Also make sure that Docker is active. Run $ docker-compose up

4)This will start:
-A MongoDB express container on port 8080
-A flask app container on port 5001

You can access MongoDB by navigating to locahost:8080 in your browser. You will be asked for login and password:
login = admin
password = pass

You will see all the databases and collections that you have.
Make sure that there is a database called 'forms' and a collection called 'templates' inside it. If those are not there then create them. The collection already has some documents inside it but you are free to add more

5)Refer to the file forms_tests.ipynb. You will see there how to make a request to the get_form endpoint inside the flask app on port 5001. 

# Inventory Management

A mini project which allows vendors to track the stocks in their stores. This project focuses on API design using Django and Django REST API.  
This project consists of the following:
1. Create database models.
2. Create API endpoints.
3. Add token authentication.
4. Testing using factories and faker.
5. Dockerize the project.

## Getting Started
### Requirements
* Python (3.9.2)
* Django (3.1.7)
* Django REST framework (3.12.4)
* factory-boy (3.2.0)
* Faker (8.1.0)
* If you want to run this using docker, you will need docker installed.

### Launch
#### Running locally
1. Use terminal and go to the project directory.
2. Run the following command to sync your database.
    ```$ python manage.py migrate```
3. Run the following command to fire up the server.
    ```$ python manage.py runserver```
4. The endpoints can be accessed at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

#### Running on Docker
1. Ensure you have docker installed.
2. Use terminal and go to the project directory.
3. Run docker compose using the command below.
    ```docker-compose up```
4. The endpoints can be accessed at [http://localhost/](http://localhost/).

## API Endpoints
### API Root Browser
This is a browserable API interface ([local](http://127.0.0.1:8000/), [docker](http://localhost/)) that allows the user to navigate to the page and perform related requests. There are 10 endpoints available.

* Endpoint for models:
    * users: [local](http://127.0.0.1:8000/users/) [docker](http://localhost/users/)
    * stores: [local](http://127.0.0.1:8000/stores/) [docker](http://localhost/stores/)
    * material-stocks: [local](http://127.0.0.1:8000/material-stocks/) [docker](http://localhost/material-stocks/)
        * cannot edit the current_capacity in `PUT` method
    * materials: [local](http://127.0.0.1:8000/materials/) [docker](http://localhost/materials/)
    * material-quantities: [local](http://127.0.0.1:8000/material-quantities/) [docker](http://localhost/material-quantities/)
    * products: [local](http://127.0.0.1:8000/products/) [docker](http://localhost/products/)

* Additional endpoints:
    * inventory: [local](http://127.0.0.1:8000/inventory/) [docker](http://localhost/inventory/)
        * allow user to `GET` details of each material with it's percentage of capacity
    * product-capacity: [local](http://127.0.0.1:8000/product-capacity/) [docker](http://localhost/product-capacity/)
        * allow user to `GET` the products with it's quantity available
    * restock: [local](http://127.0.0.1:8000/restock/) [docker](http://localhost/restock/)
        * allow user to `GET` material with it's quantity available and `POST` material with it's quantity as restock
    * sales: [local](http://127.0.0.1:8000/sales/) [docker](http://localhost/sales/)
        * allow user to `POST` product with it's quantity sold

Further details and explanation of the design of endpoints can be found [here](https://spqteam.atlassian.net/wiki/spaces/TRAIN/pages/795050022/Mini-project+Inventory+Management+WIP#Database-design%3A).

### API Token Auth
Accessed at [http://127.0.0.1:8000/api-token-auth/](http://127.0.0.1:8000/api-token-auth/) for local and [http://localhost/api-token-auth/](http://localhost/api-token-auth/) for docker.  
Only supports `POST` method for user to obtain their token by providing valid `username` and `password` for authentication. A JSON response with the token will be returned like the following.
```{ 'token' : '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b' }```

## Running the tests locally
1. Use terminal and go to the project directory.
2. Run the following command to fire up the testings.
    ```$ python manage.py test``` or
    ```$ python manage.py test --verbosity 2``` (to view result of every test)

### Tests available
There are a total of 29 tests:
* auth test
* viewsets test
	* inventory viewset
	* material stock viewset
	* product capacity viewset
	* restock viewset
	* sales viewset

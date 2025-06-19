# Django Backend Technical Test  
  
This repository contains a technical test for a senior backend Django position.  
  
## Project Structure  
  
  

your-tech-test-repo/

├── backend/ # Contains the Django project

│ ├── backend/

│ ├── cards/ # Contains the card model and views

│ ├── users/ # Contains the user model

│ ├── providers/ # Contains the provider client

│ ├── manage.py

│ └── requirements.txt

├── Dockerfile # Defines the Django application image

├── docker-compose.yml # Orchestrates the Django app and PostgreSQL database

├── .env # Environment variables for database (optional, but recommended)

└── README.md # These instructions

  
  
  

## Prerequisites  
  
To run this test, you need to have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your machine.  
  
## Setup Instructions  
  
1. **unzip the code:**  
```bash  
unzip test_senior_backend.zip
cd test_senior_backend   
```  
  
2. **(Optional but Recommended) Create a `.env` file:**  
If you don't already have one, create a file named `.env` in the root of this repository (next to `docker-compose.yml`). You can use the following default values, or change them if you prefer:  
```env  
# Database Configuration
DB_NAME=mydjangodb  
DB_USER=user  
DB_PASSWORD=password  

# Superuser Configuration (for Django Admin)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
DJANGO_SUPERUSER_EXTERNAL_ID=test_user_id_123  # Used for testing card creation
```  
  
3. **Build and run the Docker containers:**  
This command will build the Docker images (if not already built) and start the Django application (`web` service) and PostgreSQL database (`db` service) in detached mode (meaning they run in the background).  
```bash  
docker compose build  
docker compose up -d  
```  
  
4. **Run database migrations:**  
Once the containers are running, you need to apply the database migrations.  
```bash  
docker compose exec web python manage.py migrate  
```  
* `docker compose exec web`: Executes a command inside the `web` container.  
* `python manage.py migrate`: Standard Django migration command.  
  
5. **Create a superuser (optional, for accessing Django Admin):**  
If your task requires interacting with the Django admin, you might want to create a superuser.  
```bash  
docker compose exec web python manage.py createsuperuser  
```  
Follow the prompts to set up a username, email, and password.  
  
6. **Access the application:**  
Run the following command to start the Django development server:  
```bash  
docker compose exec web python manage.py runserver  
```  
The Django application should now be running and accessible in your web browser at:  
[http://localhost:8000](http://localhost:8000)  
  
If you created a superuser, the Django admin will be at [http://localhost:8000/admin/](http://localhost:8000/admin/).  
  
7. **Run tests:**  
You can run the Django test suite with the following command:  
```bash  
docker compose exec web python manage.py test  
```  
  
## Shutting Down  
  
When you are finished, you can stop and remove the containers:  
```bash  
docker compose down  
  

-   docker compose down: Stops the running containers and removes them, along with their networks. It does not remove the named volumes (like db_data), so your database data will persist. If you want to remove volumes too, add -v or --volumes.
```    

## The Task

Implement the functionality to create a debit card.
The scenario is the following:

-   Suppose the user has been already created
-   The user makes a request to create a debit card selecting only the card color. 
-   The backend calls an external provider (already mocked) to create the debit card in the provider system.
-   The backend creates the debit card in the database.
-   The backend returns the debit card to the client. 
    
Your solution should demonstrate a very strong understanding of:
1.  Clean Architecture / Domain Separation: Structure this code into logical layers.
2.  Robust Error Handling: Handle various failure scenarios, especially those originating from the external provider.
3.  Data Consistency: Ensure that the database state remains consistent even if the external provider call fails or vice-versa.
4.  Testability: Test your implementation using unit tests.
    

## Submission

Please push your solution to a new private GitHub repository or a compressed folder and share it with us. Include any relevant notes or assumptions in your README.md or a separate NOTES.md file.

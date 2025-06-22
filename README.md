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
DJANGO_SUPERUSER_PASSWORD=supersecret
DJANGO_SUPERUSER_EXTERNAL_ID=super_user_id_123

# Django secret key (use a strong, random value in production!)
DJANGO_SECRET_KEY=django-insecure-y&rw4%_p*-znsjrr=e=-w!%=kw-tu9%2dv4jl+a3%0rs7w3k0m

# Debug mode (set to False in production)
DJANGO_DEBUG=True
```  
  
3. **Build and run the Docker containers:**  
This command will build the Docker images (if not already built) and start the Django application (`web` service) and PostgreSQL database (`db` service) in detached mode (meaning they run in the background).  
```bash  
docker compose build  
docker compose up -d  
```

To view the logs:
```bash
docker compose logs -f
```
  
4. **(OPTIONAL) Run database migrations (Optional as it is now automated with Docker):**  
Once the containers are running, you need to apply the database migrations.  
```bash  
docker compose exec web python manage.py migrate  
```  
* `docker compose exec web`: Executes a command inside the `web` container.  
* `python manage.py migrate`: Standard Django migration command.  
  
5. **(OPTIONAL) Create a superuser (optional now automated with Docker, for accessing Django Admin):**  
If your task requires interacting with the Django admin, you might want to create a superuser.  
```bash  
docker compose exec web python manage.py createsuperuser  
```  
Follow the prompts to set up a username, email, and password.  
  
6. **(OPTIONAL) Access the application (optional now automated with Docker):**  
Run the following command to start the Django development server:  
```bash  
docker compose exec web python manage.py runserver  
```  
The Django application should now be running and accessible in your web browser at:  
- [http://localhost:8000](http://localhost:8000)
- The Swagger UI is available at: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- If you created a superuser, the Django admin will be at [http://localhost:8000/admin/](http://localhost:8000/admin/).
  
7. **Run tests:**  
You can run the test suite with the following command:  
```bash  
docker compose exec web pytest
```  
This will run all tests with pytest. You can also:
- Run tests with coverage report: `docker compose exec web pytest --cov=backend`
- Run specific test file: `docker compose exec web pytest tests/test_cards_api.py`
- Run tests with detailed output: `docker compose exec web pytest -v`
  
## Shutting Down  
  
When you are finished, you can use the following commands for different levels of cleanup:

```bash
# Stop and remove containers only
docker compose down

# Stop and remove containers and volumes
docker compose down -v

# Complete cleanup (containers, volumes, and images)
docker compose down -v --rmi all
```

The different cleanup options do the following:
- `docker compose down`: Stops and removes containers and networks
- `docker compose down -v`: Also removes all volumes (database data)
- `docker compose down -v --rmi all`: Removes everything including downloaded/built images

Choose the appropriate cleanup level based on your needs. For a complete project removal, use the last command.

## The Task

✅ Implementation Complete! 

The task was to implement functionality to create a debit card with the following scenario:

-   User has been already created (prerequisite)
-   User makes a request to create a debit card by selecting the card color
-   Backend calls external provider (mocked) to create the debit card
-   Backend creates the debit card in the database
-   Backend returns the debit card details to the client

### Implementation Checklist

All requirements have been successfully implemented:

- [x] **Clean Architecture / Domain Separation**
  - Implemented clear separation between API, domain logic, and data layers
  - Provider integration isolated in dedicated module
  - Service layer handling business logic

- [x] **Robust Error Handling**
  - Provider errors properly handled and mapped
  - Input validation at API level
  - Appropriate HTTP status codes and error messages
  - Graceful handling of unexpected scenarios

- [x] **Data Consistency**
  - Transaction management for database operations
  - Proper error handling for provider integration
  - Consistent state maintained between provider and local database

- [x] **Testing**
  - Comprehensive test suite implemented
  - Coverage for happy path and error scenarios
  - Provider integration tests
  - Input validation tests
  - API endpoint tests

### Additional Features
- [x] Swagger UI documentation
- [x] Comprehensive error responses
- [x] Strict contract enforcement with provider
- [x] Timezone-aware date handling

For detailed implementation notes, architecture decisions, and technical documentation, please refer to [NOTES.md](NOTES.md).

## Submission

Please push your solution to a new private GitHub repository or a compressed folder and share it with us. Include any relevant notes or assumptions in your README.md or a separate [NOTES.md](NOTES.md) file.
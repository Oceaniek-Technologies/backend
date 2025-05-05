# Getting Started with Shorties API

This guide will help you set up and run the Shorties API on your local environment.

## Prerequisites

- Python 3.8 or later
- PostgreSQL database
- pip (Python package manager)

## Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/shorties-api.git
cd shorties-api
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgres://username:password@localhost:5432/shorties
PGUSER=your_db_username
PGPASSWORD=your_db_password
PGHOST=localhost
PGPORT=5432
PGDATABASE=shorties
```

4. **Initialize the database**

```bash
python init_django.py
```

This will create all necessary database tables.

5. **Start the server**

```bash
./start.sh
```

Or, if you're on Windows:

```bash
python -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

6. **Verify the API is running**

Open your browser and navigate to:

```
http://localhost:5000/
```

You should see a message indicating that the API is running.

7. **Access the API documentation**

Navigate to:

```
http://localhost:5000/swagger/
```

This will open the Swagger UI where you can explore and test all API endpoints.

## Testing the API

You can use the provided `api_examples.py` script to test various API endpoints:

```bash
python api_examples.py
```

This script demonstrates:
- User registration
- Authentication
- Profile management
- Video upload
- Social features (likes, comments, follows)
- Notifications

## Common Issues and Solutions

### Database Connection Errors

- Make sure your PostgreSQL server is running
- Verify that the database credentials in your `.env` file are correct
- Ensure that the database specified in `PGDATABASE` exists

### Import Errors

- Verify that all dependencies have been installed with `pip install -r requirements.txt`
- Check that the Python path is correctly set up

### Permission Errors

- For file upload features, ensure that the media directory is writable
- For database operations, verify that your database user has the necessary permissions

## Development Workflow

1. Make changes to the code
2. Run migrations if you've modified models:
   ```bash
   cd shorties_api
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Restart the server to apply changes
4. Test your changes using Swagger UI or API client

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Swagger/OpenAPI Specification](https://swagger.io/specification/)

## Support

If you encounter any issues or have questions, please open an issue on the repository.
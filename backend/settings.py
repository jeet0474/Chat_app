import os

# MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

from decouple import config

# MongoDB connection
MONGO_CONNECTION_STRING = config("MONGO_CONNECTION_STRING", default="")
MONGO_DB_NAME = config("MONGO_DB_NAME", default="")


# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for development (change this for production)
CORS_ALLOWED_ORIGINS = [
    # "http://localhost:3000",  # Allow frontend requests from localhost:3000 (React app)
    "https://chat-app-ivory-iota-40.vercel.app",  # Uncomment and replace for production
]

# Middleware Configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Ensure CORS middleware is included first
    'django.middleware.common.CommonMiddleware',  # Other essential middleware
    'django.middleware.security.SecurityMiddleware',
    # other middleware...
]

# Insert CORS middleware at the beginning for proper handling of cross-origin requests
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

# Custom User Model Configuration (if you're using a custom User model)
AUTH_USER_MODEL = 'users.User'  # Make sure to define a custom user model if you're using one

# Installed Apps (Add your apps and third-party apps)
INSTALLED_APPS = [
    # Default Django apps...
    'users',  # Your custom user app
    # 'user_connections',
    'corsheaders',  # CORS handling
    # other installed apps...
    
    "channels",
    
    "backend",
]

WSGI_APPLICATION = 'backend.wsgi.application'

ASGI_APPLICATION = "backend.asgi.application"

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")
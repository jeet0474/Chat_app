# MongoDB Configuration (Use djongo or mongoengine for MongoDB connection)
# MONGO_CONNECTION_STRING = "mongodb+srv://jeet0474:Md_jeet0474@jeet.v42ik.mongodb.net/"
# MONGO_DB_NAME = "test"

import os

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")


# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for development (change this for production)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Allow frontend requests from localhost:3000 (React app)
    #"https://your-production-domain.com",  # Uncomment and replace for production
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

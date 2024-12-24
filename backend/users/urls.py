from django.urls import path
from .views import create_user, get_users, search_users, get_user_connections, login_user
# from .views import create_user, get_users, search_users, get_user_connections, login_user, get_conversation_messages, handle_conversation_and_message, get_conversation, remove_active_user

urlpatterns = [
    path("create_user/", create_user, name="create_user"),
    path("login_user/", login_user, name="login_user"),
    path("get_users/", get_users, name="get_users"),
    path("search_users/", search_users, name="search_users"),
    path("get_user_connections/", get_user_connections, name="get_user_connections"),
]

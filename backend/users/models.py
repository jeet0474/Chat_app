from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, ListField, ReferenceField, EmbeddedDocumentField
from datetime import datetime
from bson import ObjectId

class Connection(EmbeddedDocument):
    """
    Connection model to represent a connection between a user and another user, with an image link.
    """
    connectionId = ReferenceField('User', required=True)  # Reference to another User
    name = StringField(required=True)  # Connection name
    image_link = StringField(default="")  # Image link for the connection (can be empty or a URL)

    def to_json(self):
        return {
            "connectionId": str(self.connectionId.id),  # Convert ObjectId to string
            "connectionName": self.name,
            "image_link": self.image_link  # Include image link for the connection
        }

class User(Document):
    """
    User model to represent user details, their connections, and their image link.
    """
    meta = {"collection": "users"}  # Define the MongoDB collection name
    
    username = StringField(required=True, max_length=100, unique=True)  # User's username
    password = StringField(required=True, max_length=255)  # User's password
    image_link = StringField(default="")  # Image link (can be an empty string or URL)
    createdAt = DateTimeField(default=datetime.utcnow)  # User creation timestamp
    connections = ListField(EmbeddedDocumentField(Connection))  # List of user connections

    # Method to convert a user document to JSON
    def to_json(self):
        return {
            "username": self.username,
            "created_at": self.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
            "image_link": self.image_link,  # Include image link for the user
            "connections": [conn.to_json() for conn in self.connections],  # Include connections
        }

    # Cascade delete handling: Delete associated connections and chats (if needed)
    def delete(self, *args, **kwargs):
        # First, delete all connections in the user's list
        for conn in self.connections:
            conn.connectionId.delete()  # Remove associated connections if needed
        
        # Delete associated chats (you will need a Chat model)
        # Assuming there's a Chat model, and we delete all chats where the user is involved
        # from .chat import Chat
        # Chat.objects(senderId=self.id).delete()
        # Chat.objects(receiverId=self.id).delete()

        # Now delete the user document itself
        super().delete(*args, **kwargs)


class Message(EmbeddedDocument):
    """
    Message model to represent a message within a conversation.
    The timestamp will be set to the current time (Date).
    """
    senderId = ReferenceField('User', required=True)  # Reference to the sender
    message = StringField(required=True)  # Message content
    timestamp = DateTimeField(default=datetime.utcnow)  # Store the timestamp as Date (current UTC time)

    def to_json(self):
        return {
            "senderId": str(self.senderId.id),  # Convert ObjectId to string
            "message": self.message,
            "timestamp": self.timestamp.isoformat()  # Return timestamp as ISO formatted string
        }
        
class Conversation(Document):
    """
    Conversation model to represent a conversation between two users.
    """
    meta = {"collection": "conversations"}  # MongoDB collection name
    
    user1 = ReferenceField('User', required=True)  # First user in the conversation
    user2 = ReferenceField('User', required=True)  # Second user in the conversation
    messages = ListField(EmbeddedDocumentField(Message))  # List of messages in the conversation
    createdAt = DateTimeField(default=datetime.utcnow)  # Timestamp of conversation creation
    updatedAt = DateTimeField(default=datetime.utcnow)  # Timestamp of last update

    def to_json(self):
        return {
            "user1": str(self.user1.id),
            "user2": str(self.user2.id),
            "messages": [msg.to_json() for msg in self.messages],
            "createdAt": self.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
            "updatedAt": self.updatedAt.strftime("%Y-%m-%d %H:%M:%S")
        }

    def add_message(self, sender, message_content):
        """
        Method to add a new message to the conversation.
        """
        message = Message(senderId=sender, message=message_content)
        self.messages.append(message)
        self.updatedAt = datetime.utcnow()  # Update the last updated timestamp
        self.save()


# Assuming a method to create a new conversation between two users
def create_conversation(user1, user2):
    """
    Function to create a new conversation between two users.
    """
    conversation = Conversation(user1=user1, user2=user2)
    conversation.save()
    return conversation

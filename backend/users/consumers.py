import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from redis.asyncio import Redis
from pymongo import MongoClient
from bson import ObjectId
from redis.exceptions import ConnectionError
from channels.layers import get_channel_layer
from dotenv import load_dotenv
import os

from decouple import config

# MongoDB connection
MONGO_CONNECTION_STRING = config("MONGO_CONNECTION_STRING", default="")
MONGO_DB_NAME = config("MONGO_DB_NAME", default="")

# Load environment variables from .env file
# load_dotenv()

# MongoDB Configuration
# MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Redis Configuration
# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = int(os.getenv("REDIS_PORT"))
# REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default="6379")
REDIS_PASSWORD = config("REDIS_PASSWORD", default="")

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Initialize Redis connection
        self.redis = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )

        # Connect to MongoDB
        self.mongo_client = MongoClient(MONGO_CONNECTION_STRING)
        self.db = self.mongo_client[MONGO_DB_NAME]
        self.conversations_collection = self.db["conversations"]

        # Parse query parameters
        query_params = self.scope["query_string"].decode()
        self.user_id = query_params.split("=")[1].split("&")[0]
        self.other_user_id = query_params.split("=")[2]

        # Generate the canonical Redis channel key (sorting user IDs)
        sorted_ids = sorted([self.user_id, self.other_user_id])
        self.redis_channel = f"chat_{sorted_ids[0]}_{sorted_ids[1]}"

        # Accept the WebSocket connection
        await self.accept()

        # Call update_active_users to remove user from previous chats
        await self.update_active_users()

        # Fetch old messages from Redis
        # cached_messages = await self.redis.hget(self.redis_channel, "old_messages")

        # Check if the Redis key exists
        key_exists = await self.redis.exists(self.redis_channel)

        if key_exists:
            # Now check if "old_messages" exists within the hash
            old_messages_exists = await self.redis.hexists(self.redis_channel, "old_messages")

            if old_messages_exists:
                cached_messages = await self.redis.hget(self.redis_channel, "old_messages")
                self.old_messages = json.loads(cached_messages) if cached_messages else []
            else:
                self.old_messages = []  # Key exists, but "old_messages" is missing
        else:
            # If no cached messages, fetch from MongoDB and store in Redis
            self.old_messages = await self.load_messages()

            if self.old_messages:
                await self.redis.hset(self.redis_channel, "old_messages", json.dumps(self.old_messages))
                await self.redis.expire(self.redis_channel, 86400)  # Set TTL to 24 hours

        # Fetch new messages from Redis
        new_messages = await self.redis.hget(self.redis_channel, "new_messages")
        try:
            self.new_messages_list = json.loads(new_messages) if new_messages else []
        except json.JSONDecodeError:
            self.new_messages_list = []

        # Combine old and new messages
        all_messages = self.old_messages + self.new_messages_list

        # Send combined messages to the frontend
        await self.send(json.dumps({"type": "old_messages", "messages": all_messages}))

        # Subscribe to Redis channel for this chat room
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.redis_channel)

        # Start a task to listen for messages from Redis
        asyncio.create_task(self.listen_for_redis_messages())


    async def disconnect(self, close_code):
        # Mark users as inactive in Redis (remove user from active list)
        await self.update_active_users(remove_user=True)

        # Close Redis and MongoDB connections
        await self.redis.close()
        self.mongo_client.close()

        # Unsubscribe from Redis channel
        await self.pubsub.unsubscribe(self.redis_channel)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json["type"] == "new_message":
            message_content = text_data_json["message"]

            # Save message to Redis and MongoDB
            await self.save_message(message_content)

            # Publish message to Redis channel
            await self.redis.publish(
                self.redis_channel,
                json.dumps({"type": "new_message", "message": {"senderId": self.user_id, "message": message_content}})
            )
        elif text_data_json["type"] == "ping":
            await self.send(json.dumps({"type": "pong"}))

    async def listen_for_redis_messages(self):
        while True:  # Retry indefinitely if the connection is lost
            try:
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        message_data = json.loads(message["data"])

                        # Send the message to the WebSocket client
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "new_message",
                                    "message": message_data["message"],
                                }
                            )
                        )
            except ConnectionError as e:
                print(f"Redis connection lost: {e}. Reconnecting...")
                await asyncio.sleep(5)  # wait before trying to reconnect
                try:
                    # Reconnect to the Redis pubsub
                    await self.pubsub.unsubscribe(self.redis_channel)
                    self.pubsub = self.redis.pubsub()
                    await self.pubsub.subscribe(self.redis_channel)
                except Exception as ex:
                    print(f"Failed to reconnect to Redis: {ex}")
                    await asyncio.sleep(5)  # back off before retrying

    async def save_message(self, message_content):
        """
        Save a message to Redis and MongoDB, create a conversation if it doesn't exist,
        and update the connections array in the users collection.
        """
        message_data = {
            "senderId": self.user_id,
            "message": message_content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Save to Redis (append to new_messages field)
        new_messages = await self.redis.hget(self.redis_channel, "new_messages")
        new_messages_list = json.loads(new_messages) if new_messages else []
        new_messages_list.append(message_data)

        # Create or update the conversation in MongoDB
        conversation = await asyncio.to_thread(
            self.conversations_collection.find_one,
            {
                "$or": [
                    {"user1": ObjectId(self.user_id), "user2": ObjectId(self.other_user_id)},
                    {"user1": ObjectId(self.other_user_id), "user2": ObjectId(self.user_id)},
                ]
            }
        )

        if not conversation:
            # Conversation doesn't exist, create one
            conversation_data = {
                "user1": ObjectId(self.user_id),
                "user2": ObjectId(self.other_user_id),
                "messages": [message_data],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }

            # Insert the conversation
            conversation_result = await asyncio.to_thread(
                self.conversations_collection.insert_one,
                conversation_data
            )
            conversation_id = conversation_result.inserted_id

            # Update connections for both users
            await self.update_connections(self.user_id, self.other_user_id)
            
        else:
            # Conversation exists, just update the messages
            await asyncio.to_thread(
                self.conversations_collection.update_one,
                {
                    "_id": conversation["_id"]
                },
                {
                    "$push": {"messages": message_data},
                    "$set": {"updatedAt": datetime.utcnow()},
                }
            )

        # Update Redis with new messages
        await self.redis.hset(self.redis_channel, "new_messages", json.dumps(new_messages_list))

    async def load_messages(self):
        """
        Load old messages from MongoDB and cache them in Redis.
        """
        try:
            # Fetch conversation from MongoDB
            conversation = await asyncio.to_thread(
                self.conversations_collection.find_one,
                {
                    "$or": [
                        {"user1": ObjectId(self.user_id), "user2": ObjectId(self.other_user_id)},
                        {"user1": ObjectId(self.other_user_id), "user2": ObjectId(self.user_id)},
                    ]
                }
            )

            if not conversation or "messages" not in conversation:
                return []

            # Process messages
            old_messages = [
                {
                    "senderId": str(msg["senderId"]),
                    "message": msg["message"],
                    "timestamp": msg["timestamp"].isoformat() if isinstance(msg["timestamp"], datetime) else msg["timestamp"],
                }
                for msg in conversation["messages"]
            ]
            
            return old_messages

        except Exception as e:
            return []

    async def append_messages_to_mongo(self, new_messages_list):
        """
        Append new messages to the MongoDB conversation.
        """
        try:
            # Search for the conversation between the users in MongoDB
            conversation = await asyncio.to_thread(
                self.conversations_collection.find_one,
                {
                    "$or": [
                        {"user1": ObjectId(self.user_id), "user2": ObjectId(self.other_user_id)},
                        {"user1": ObjectId(self.other_user_id), "user2": ObjectId(self.user_id)},
                    ]
                }
            )

            if conversation:
                # Append new messages to the existing conversation document
                await asyncio.to_thread(
                    self.conversations_collection.update_one,
                    {
                        "_id": conversation["_id"]
                    },
                    {
                        "$push": {"messages": {"$each": new_messages_list}}
                    }
                )

            # Clear the Redis "new_messages" cache for this conversation after appending to MongoDB
            await self.redis.hdel(self.redis_channel, "new_messages")
        except Exception as e:
            print(f"Error appending messages to MongoDB: {e}")
            
    async def update_active_users(self, remove_user=False):
        """
        Update active users in Redis.
        - Removes the user from all previous active lists in other channels.
        - Deletes Redis keys with empty active_users lists.
        - Adds the user to the current chat's active_users list.
        """
        try:
            # Fetch all chat keys
            keys = await self.redis.keys("chat_*")

            for key in keys:
                # Get the active_users for the current key
                active_users = await self.redis.hget(key, "active_users")
                if active_users:
                    try:
                        # Parse active_users JSON
                        active_users_list = json.loads(active_users)

                        if isinstance(active_users_list, list):
                            # Remove the user ID if present
                            if self.user_id in active_users_list:
                                active_users_list.remove(self.user_id)

                            if active_users_list:
                                # Update the active_users field if the list is not empty
                                await self.redis.hset(key, "active_users", json.dumps(active_users_list))
                            else:
                                # Delete the key if the list is empty
                                await self.redis.delete(key)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding active_users for key {key}: {e}")

            # Add the user to the current chat's active_users
            active_users = await self.redis.hget(self.redis_channel, "active_users")
            try:
                active_users_list = json.loads(active_users) if active_users else []
                if self.user_id not in active_users_list:
                    active_users_list.append(self.user_id)
            except json.JSONDecodeError:
                # If decoding fails, start with a new list containing only the user ID
                active_users_list = [self.user_id]

            # Update Redis with the new active_users list for the current chat
            await self.redis.hset(self.redis_channel, "active_users", json.dumps(active_users_list))
        except Exception as e:
            print(f"Error updating active users: {e}")
            
    async def update_connections(self, user_id, other_user_id):
        """
        Update the connections array for both users in the users collection.
        This ensures both users have each other in their connections array.
        """
        # Get user details (names, images, etc.) - assuming you already have these fields available
        user = await asyncio.to_thread(self.db["users"].find_one, {"_id": ObjectId(user_id)})
        other_user = await asyncio.to_thread(self.db["users"].find_one, {"_id": ObjectId(other_user_id)})

        if user and other_user:
            user_connection = {
                "connectionId": ObjectId(other_user["_id"]),
                "connectionName": other_user["username"],
                "image_link": other_user["image_link"]
            }

            other_user_connection = {
                "connectionId": ObjectId(user["_id"]),
                "connectionName": user["username"],
                "image_link": user["image_link"]
            }

            # Update the connections array in both users' documents
            await asyncio.to_thread(
                self.db["users"].update_one,
                {"_id": ObjectId(user_id)},
                {"$push": {"connections": user_connection}}
            )

            await asyncio.to_thread(
                self.db["users"].update_one,
                {"_id": ObjectId(other_user_id)},
                {"$push": {"connections": other_user_connection}}
            )

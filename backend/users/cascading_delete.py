from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb+srv://jeet0474:Md_jeet0474@jeet.v42ik.mongodb.net/?retryWrites=true&w=majority&appName=Jeet')
db = client.chat_app
users_collection = db.user
connections_collection = db.connection
chats_collection = db.chat

change_stream = users_collection.watch([{'$match': {'operationType': 'delete'}}])

print("Listening for user deletions...")
for change in change_stream:
    try:
        user_id = change['documentKey']['_id']

        # Delete connections and chats associated with the user
        connections_collection.delete_many({'user': ObjectId(user_id)})
        chats_collection.delete_many({
            '$or': [
                {'sender': ObjectId(user_id)},
                {'receiver': ObjectId(user_id)}
            ]
        })

        print(f"Cascading deletes for user {user_id} completed.")
    except Exception as e:
        print(f"Error during cascading delete: {e}")

from pymongo import MongoClient
import threading

def watch_user_deletions():
    client = MongoClient("mongodb+srv://jeet0474:Md_jeet0474@jeet.v42ik.mongodb.net/?retryWrites=true&w=majority&appName=Jeet")
    db = client.chat_app  # Replace with your database name
    user_change_stream = db.users.watch([{ "$match": { "operationType": "delete" } }])

    for change in user_change_stream:
        deleted_user_id = change["documentKey"]["_id"]
        print(f"User {deleted_user_id} deleted. Performing cascading deletes...")

        # Delete associated connections and chats
        db.connections.delete_many({"userId": deleted_user_id})
        db.chats.delete_many({
            "$or": [
                {"senderId": deleted_user_id},
                {"receiverId": deleted_user_id}
            ]
        })
        print(f"Associated data for user {deleted_user_id} deleted successfully.")

# Run the watcher in a background thread
thread = threading.Thread(target=watch_user_deletions, daemon=True)
thread.start()

from pymongo import MongoClient
from django.http import JsonResponse
from django.conf import settings  # To access settings variables
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from bson import ObjectId
import bcrypt  # For password hashing
import jwt  # For JWT token generation
import random
from .models import User  # Import the Conversation, User, and Message models
import logging
from .stk_scraper import get_google_finance_price

imageLinks = [
    # First Set of Image links for users
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461885/12980762_5096160_w3q7vv.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461884/solo_for_phone1_wanhmz.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461884/pxfuel_3_xx0eh4.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461883/man_odbyw3.png",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461883/fd54cf3464965fe5b05ec05001604125_l9kpcp.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461882/f84b90ae23439b14fa588b0f658512bb_hvfvjs.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461882/e8cce00da66cafe28b449c474ff0b3a6_m0lltf.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461881/e8a6f5579f55fbd4c68a9d73c8d6914d_zags1n.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461881/d01d877158c915fcf6d043faa055e5f9_tu8l3k.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461881/c54890ca49bf3a5017cf557e8d7a8b3c_p38spn.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461880/beccf85100b9392824f6c41ad9709c68_lr4t6a.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461879/b3fb273e80087f1b421993f8f3f1b258_wpvvpg.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461879/a7216d6c9edff084b1d12255c6fb40c4_xjrkts.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461878/5833463fcd4acb4f2a7541e29867731b_aeq21v.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461878/900343ad64c6ce209f863a63f9535d51_u4diek.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461877/42b821b2e39438aea2e3528147fb92e6_plbpbu.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461877/42ab78775cfd43c66fa0fae3dac27346_ludltk.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461877/8dd338bcdfca07af51efe72ad58606d7_rdan7e.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461877/_e2f3cb6d-5ef9-4842-9562-2f78c7f9a740_kmaddr.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734461876/_947dcc0d-eed4-4889-ae14-f0b0a7c6d5cd_bczhox.jpg",
    # Second Set of Image links for users
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642281/e83e24876ec139dea4896a70649c0084_zidzd2.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642280/9312d77188b0c7f510364b7646d6a2bb_qgkw9c.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642280/88d6a677457eeb6db1065de0fd13b34c_rziqzb.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642280/817d9c5bfe0e0be0fe350b3adb580335_ekl3nd.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642279/f432692000a917cf3694ea305535bb22_scfnbr.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642279/90b9412f2a72baa1a232c8d4e774520a_xuwrdq.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642279/280d0a7435923f4a87535c362ec7b9fd_ogoe6r.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642279/69dcd3a2f291b4c943dadafd8ac3614d_z27one.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642279/64f374522d644552a7474e29128ed18e_jtyloq.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642278/52e6fbbfd231934ff99db1574f238638_dwjnuw.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642278/8f5c17b2a4368f42a5a61ee2b74e9fec_qyvr7f.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642278/55a6aa00e335de95102de58a47c708cd_ceekik.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642278/760f52d4ba26e74c5497721534ed81eb_g3jzk2.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642278/4c9147c1f6165da873a9d857b83ea14d_aof56w.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642277/c253bcfeac8c2865d0fc87bc0b1416df_tfh3w9.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642277/4d5fa8c56f5b67c43136f74f9d367fdc_x57hgk.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642277/6cf2bf3de48ac12d1f5d6645e509e4d6_qwn8x7.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642277/0b6022264df13dac2ae50b9293976155_t3kcbc.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642277/dc00a592a508c3a97c5454aa1a167856_s2pwsy.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642276/f87d35a4b0e87fe395ffe14508619829_foerog.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642276/e720119b2f4683a8f8dbc49936869867_swsoob.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642276/5631fa00317a9f44d929848397845f66_dbvmxe.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642276/1502630d83074aea1e92d9f5ba608923_t06f80.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642276/b4656768a9fbae8e3c58dffd0f2e85cc_ikuksn.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642275/cf2a5c027e1e6e8378bf920ee05a7b53_nmoynj.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642275/c5643a0780e051eac69da46d79cba8f7_if9d71.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734642275/b74f5ec2ba13345b5feceee834761bba_vmks8q.jpg",
    # Third Set of Image links for users
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684415/d85ff304000484d87d7151a7e9b160b4_jnhbkm.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684415/176b6a9175b047adb3cafc737b81319d_daxx3g.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684415/aa02dca113051226993aded111a508bb_s1mips.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684415/7788198876fb2055491b1cdbd6321ed5_ul0zyp.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684415/886370868cb33e1449c190ff3c39d207_idejf7.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684414/009005982ce3b10aee2653b25112eb6d_epn7p6.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684414/94988f061d25b1e5f496ec8868d7f250_win4zg.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684413/44642fd0b06167928e2ed948d181f355_zn39yj.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684413/771c5b92f82073d5e6d49a48603df78a_ljvdms.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/75b46417bca0a5c408567122006bc03d_op7qbt.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684413/665aea983c90e21a4cda5d93c5dcff0d_dxpb15.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684413/2032ca3f00d801445fe20fd0d0e055ad_y1ou7d.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/499d1aaf515492c67df286da596e2db7_kkskej.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/648e463f3084a9b6c746f56bd015263c_wujs0k.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/75ff6578b498f88dc509022dbb0d9810_vhvfc2.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/376f029d387602ed05e3ce0936375add_nzjtsp.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/9ef1310ee63a3e1dd5ffac6c7dc72eb9_xyd1kh.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/8d9403b5eaa233cef67ee9af8b1e2ddd_itxfkr.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/71f5290483edf0e3abd829ce4982414b_ybykwl.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/50d44bdec733e4c5ad860f441cc90b55_htisv3.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/a5f8a6d6c02976d90365c20c3cfb8a9c_ocsm4f.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684412/5e9c76ade1ffa3ca11af9c30b7aba670_hzffzb.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/0676ef62fef5b9c2005096dda5db4867_kpb9rr.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/05466b76f523e679aa8508152820b2a3_wyyd4y.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/14fba22f36fa938934fb89ea89449531_l1yt3a.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/4e7c7d26bdcbb62147385776c11b68ae_lgmlvf.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/9f72f73aec58231528ae424a82f3ffb1_loquud.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/53f7a93bbffe74987a4d5ce2919a8b66_yekr7l.jpg",
    "https://res.cloudinary.com/dmhk6kfhi/image/upload/v1734684411/8d68dbfb4c528cc6068fe71e9bb47a95_sledh2.jpg"
]


@csrf_exempt
def login_user(request):
    """
    Authenticate a user and fetch their data from the MongoDB database.
    """
    if request.method == "POST":
        try:
            # Access MongoDB settings
            connection_string = settings.MONGO_CONNECTION_STRING
            database_name = settings.MONGO_DB_NAME

            # Parse request body
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            # Validate inputs
            if not username or not password:
                return JsonResponse({"error": "Username and password are required."}, status=400)

            # Connect to MongoDB
            client = MongoClient(connection_string)
            db = client[database_name]
            users_collection = db["users"]

            # Find the user by username
            user = users_collection.find_one({"username": username})
            if not user:
                return JsonResponse({"error": "Invalid username or password."}, status=401)

            # Verify the hashed password
            hashed_password = user.get("password")
            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return JsonResponse({"error": "Invalid username or password."}, status=401)

            # Prepare user data for response
            user_data = {
                "username": user["username"],
                "created_at": user["createdAt"].strftime("%Y-%m-%d %H:%M:%S"),
                "_id": str(user["_id"]),  # Convert ObjectId to string
            }

            return JsonResponse({"message": "Login successful!", "user": user_data}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid HTTP method. Only POST is allowed."}, status=405)

@csrf_exempt
def create_user(request):
    """
    Create a new user in the MongoDB database using pymongo,
    with a randomly assigned image link and hashed password.
    """
    if request.method == "POST":
        try:
            # Parse request body
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            # Validate input
            if not username or not password:
                return JsonResponse({"error": "Username and password are required."}, status=400)

            # Connect to MongoDB
            client = MongoClient(settings.MONGO_CONNECTION_STRING)
            db = client[settings.MONGO_DB_NAME]
            users_collection = db["users"]

            # Ensure the username field is indexed
            users_collection.create_index("username", unique=True)

            # Check if the username already exists
            if users_collection.find_one({"username": username}):
                return JsonResponse({"error": "Username already exists."}, status=409)  # HTTP 409 Conflict

            # Assign a random image link to the user
            image_link = random.choice(imageLinks)

            # Hash the password with an optimized cost factor
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10))

            # Create and insert the new user
            user = {
                "username": username,
                "password": hashed_password,  # Store password as bytes
                "image_link": image_link,
                "createdAt": datetime.utcnow(),
                "connections": [],  # Empty connections array (can be updated later)
            }

            # Insert the user into the users collection
            users_collection.insert_one(user)

            # Return success response
            return JsonResponse({"message": "User created successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method. Only POST is allowed."}, status=405)


def get_users(request):
    """
    Fetch all users from the MongoDB database using pymongo.
    """
    if request.method == "GET":
        try:
            # Access MongoDB settings from settings.py
            connection_string = settings.MONGO_CONNECTION_STRING
            database_name = settings.MONGO_DB_NAME

            # Connect to MongoDB
            client = MongoClient(connection_string)
            db = client[database_name]
            users_collection = db["users"]

            # Query MongoDB
            users = users_collection.find()
            users_list = [
                {
                    "username": user["username"],
                    "created_at": user["createdAt"].strftime("%Y-%m-%d %H:%M:%S"),
                    "image_link": user.get("image_link", "")  # Fetch image_link, default to empty string if not present
                }
                for user in users
            ]
            return JsonResponse(users_list, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method. Only GET is allowed."}, status=405)



def search_users(request):
    """
    Fetch users based on search query, excluding the current user and their connections.
    """
    if request.method == "GET":
        try:
            # Access MongoDB settings from settings.py
            connection_string = settings.MONGO_CONNECTION_STRING
            database_name = settings.MONGO_DB_NAME

            # Connect to MongoDB
            client = MongoClient(connection_string)
            db = client[database_name]
            users_collection = db["users"]

            # Get query parameters
            query = request.GET.get("query", "").strip()
            current_user_id = request.GET.get("current_user_id", "").strip()

            # If no query, return an empty list
            if not query:
                return JsonResponse([], safe=False, status=200)

            if not current_user_id:
                return JsonResponse({"error": "Current user ID is required."}, status=400)

            # Convert current_user_id to ObjectId
            from bson import ObjectId
            try:
                current_user_object_id = ObjectId(current_user_id)
            except Exception:
                return JsonResponse({"error": "Invalid current user ID."}, status=400)

            # Fetch the current user's connections
            current_user = users_collection.find_one({"_id": current_user_object_id})
            if not current_user:
                return JsonResponse({"error": "Current user not found."}, status=404)

            # Get the list of connection IDs
            connection_ids = [conn["connectionId"] for conn in current_user.get("connections", [])]

            # Build the query to filter users
            users = users_collection.find({
                "$and": [
                    {"username": {"$regex": query, "$options": "i"}},  # Match the search query
                    {"_id": {"$ne": current_user_object_id}},  # Exclude the current user
                    {"_id": {"$nin": connection_ids}}  # Exclude connections
                ]
            })

            # Build the response to include username, image_link, and id
            users_list = []
            for user in users:
                user_data = {
                    "id": str(user["_id"]),  # Include the user's ID (converted to string)
                    "username": user["username"],
                    "image_link": user.get("image_link", ""),  # Include the user's image_link
                }
                users_list.append(user_data)

            return JsonResponse(users_list, safe=False, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method. Only GET is allowed."}, status=405)



def get_user_connections(request):
    """
    Fetch all connections of a user from the MongoDB database using pymongo.
    """
    if request.method == "GET":
        try:
            # Get username from query parameters
            username = request.GET.get("username")
            if not username:
                return JsonResponse({"error": "Username is required."}, status=400)

            # Access MongoDB settings from settings.py
            connection_string = settings.MONGO_CONNECTION_STRING
            database_name = settings.MONGO_DB_NAME

            # Connect to MongoDB
            client = MongoClient(connection_string)
            db = client[database_name]
            users_collection = db["users"]

            # Find the user by username
            user = users_collection.find_one({"username": username})

            if not user:
                return JsonResponse({"error": "User not found."}, status=404)

            # Extract connections
            connections = user.get("connections", [])
            connections_list = [
                {
                    "connectionId": str(conn["connectionId"]),  # Convert ObjectId to string
                    "name": conn.get("connectionName", "Unknown Name"),  # Use "connectionName" instead of "name"
                    "image_link": conn.get("image_link", "")  # Fetch image_link for each connection, default to empty string
                }
                for conn in connections
            ]

            return JsonResponse({"connections": connections_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method. Only GET is allowed."}, status=405)

@csrf_exempt
def get_stock_price(request):
    """
    Fetch stock price data from Google Finance.
    GET endpoint that accepts 'stock' and 'exchange' query parameters.
    
    Query Parameters:
        - stock: Stock symbol (e.g., "HINDCOPPER")
        - exchange: Exchange code (e.g., "NSE", "BSE")
    
    Example: /get_stock_price/?stock=HINDCOPPER&exchange=NSE
    """
    if request.method == "GET":
        try:
            # Get query parameters
            stock = request.GET.get("stock", "").strip()
            exchange = request.GET.get("exchange", "").strip()
            
            # Validate parameters
            if not stock:
                return JsonResponse(
                    {"error": "Stock symbol is required", "success": False},
                    status=400
                )
            
            if not exchange:
                return JsonResponse(
                    {"error": "Exchange is required", "success": False},
                    status=400
                )
            
            # Fetch stock data
            stock_data = get_google_finance_price(stock, exchange, max_attempts=3)
            
            # Return response
            if stock_data.get("success"):
                return JsonResponse(stock_data, status=200)
            else:
                return JsonResponse(stock_data, status=404)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_stock_price: {type(e).__name__}: {e}")
            return JsonResponse(
                {
                    "error": f"Server error: {type(e).__name__}",
                    "success": False
                },
                status=500
            )
    
    return JsonResponse(
        {"error": "Invalid HTTP method. Only GET is allowed.", "success": False},
        status=405
    )
import os
import json
import psycopg2
import hashlib
import base64
import time
import testevents as mock
from datetime import datetime, timezone
import data_validators as valid
from dotenv import load_dotenv

load_dotenv()


"""
API code for all endpoints, may split into more files at some point
"""
start_time = time.time()
db_host = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_port = os.environ["DB_PORT"]

mock.create_post_event  # just did is just to stop linting error from bothering

get_user_by_username = "/users/username"
user_create = "/users/create"
user_auth = "/users/auth"

get_post_by_id = "/posts/id"
post_create = "/posts/create"

follow_path = "/relationships/follow"
unfollow_path = "/relationships/unfollow"

feed_new = "/feed/new"
feed_followed = "/feed/followed"

conn = psycopg2.connect(
    host=db_host, dbname=db_name, user=db_user, password=db_password, port=db_port
)
cursor = conn.cursor()


def lambda_handler(event, context):
    """
    Handles all path from event object
    """
    method = event.get("httpMethod")
    path = event.get("path")

    if "queryStringParameters" not in event:
        event["queryStringParameters"] = {}
    if "body" not in event:
        event["body"] = {}
    if "pathParameters" not in event:
        event["pathParameters"] = {}

    try:
        if path.startswith("/users"):
            if path.startswith(get_user_by_username) and method == "GET":
                return get_user(event)
            elif path == user_create and method == "POST":
                return create_user(event)
            elif path == user_auth and method == "POST":
                return validate_user(event)
            else:
                splits = path.split("/")
                if len(splits) == 3:
                    if method == "DELETE":
                        return delete_user(event)
                elif len(splits) == 4:
                    if splits[3] == "posts" and method == "GET":
                        return get_user_posts(event)
                    elif splits[3] == "followers" and method == "GET":
                        return get_user_followers(event)
                    elif splits[3] == "following" and method == "GET":
                        return get_user_following(event)

        elif path.startswith("/posts"):
            if path.startswith(get_post_by_id) and method == "GET":
                return get_post(event)
            elif path == post_create and method == "POST":
                return create_post(event)
            else:
                splits = path.split("/")
                if len(splits) == 4:
                    if splits[3] == "comment" and method == "GET":
                        return get_comments(event)
                    elif splits[3] == "comment" and method == "POST":
                        return post_comment(event)

        elif path.startswith("/relationships"):
            if path == follow_path and method == "POST":
                return follow(event)
            elif path == unfollow_path and method == "POST":
                return unfollow(event)

        elif path.startswith("/feed"):
            if path == feed_new and method == "GET":
                return get_feed_new(event)
            elif path.startswith(feed_followed) and method == "GET":
                return get_feed_followed(event)

        return build_response(400, {"msg": "Not implemented for this endpoint"})

    except NotImplementedError:
        # This is just for testing: It will be Exception as e #
        return build_response(500, {"msg": type("e").__name__})

    finally:
        cursor.close()
        conn.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Took {elapsed_time:.4f} seconds to execute.")


def create_user(e):
    """
    Create a new user for users table
    """
    BODY = e["body"]

    if not valid.create_user(BODY):
        print("error:", valid.create_user.errors)  # remove these later
        return build_response(400, {"msg": "Error in body"})

    password = BODY["password"]
    username = BODY["username"]

    statement = "SELECT * FROM users WHERE username = %s"
    cursor.execute(statement, (username,))
    check = cursor.fetchone()
    # Make sure username is unique
    if check:
        return build_response(400, {"msg": "Username is taken"})

    # Encode password by creating salt
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 10000
    )
    hash = base64.b64encode(salt + hashed_password).decode("utf-8")

    statement = (
        "INSERT INTO users (username,password_hash) VALUES(%s,%s) RETURNING user_id"
    )
    cursor.execute(statement, (username, hash))
    conn.commit()
    new_id = cursor.fetchone()[0]

    return build_response(200, {"msg": "Sucessfully added", "new_user_id": new_id})


def get_user(e):
    """
    Get a user by username
    """
    PP = e["pathParameters"]
    QSP = e['queryStringParameters']
    params = {'username': PP.get('username','error')}
    if 'user' in QSP:
        params['user_id'] = QSP['user']
        if not user_exists(QSP['user']):
            return build_response(404,'Query user not found')

    if not valid.get_user.validate(params):
        print(valid.get_user.errors)
        return build_response(400, {"msg": "Error in parameters"})


    username = params["username"]

    if 'user_id' in params:
        
        user_id = params['user_id']
        statement = """
        SELECT user_id,
        (
            SELECT COUNT(*)
            FROM follows
            WHERE follower_id = user_id
        ) AS following_ct,
        (
            SELECT COUNT(*)
            FROM follows
            WHERE followee_id = user_id
        ) AS followers_ct,
        CASE WHEN f1.follower_id IS NOT NULL THEN TRUE ELSE FALSE END AS following_me,
        CASE WHEN f2.follower_id IS NOT NULL THEN TRUE ELSE FALSE END AS am_following
        FROM users u
        LEFT JOIN follows f1 on f1.follower_id = user_id AND f1.followee_id = %s
        LEFT JOIN follows f2 on f2.follower_id = %s AND f2.followee_id = u.user_id

        WHERE username = %s;
        """

        cursor.execute(statement, (user_id,user_id,username))
        res = cursor.fetchone()
        # See if item exists
        if res is None:
            return build_response(404, {"msg": "User does not exist"})

        user = {
            "username": username,
            "user_id": res[0],
            "followers_ct": res[2],
            "following_ct": res[1],
            "msg": "Success",
            "following_me": res[3],
            "am_following": res[4],
        }
        return build_response(200, user)
    else:
        statement = """
        SELECT user_id,
        (
            SELECT COUNT(*)
            FROM follows
            WHERE follower_id = user_id
        ) AS following_ct,
        (
            SELECT COUNT(*)
            FROM follows
            WHERE followee_id = user_id
        ) AS followers_ct
        FROM users 
        WHERE username = %s;
        """

        cursor.execute(statement, (username,))
        res = cursor.fetchone()
        # Check if the username exists
        if res is None:
            return build_response(404, {"msg": "User does not exist"})

        user = {
            "username": username,
            "user_id": res[0],
            "followers_ct": res[2],
            "following_ct": res[1],
            "msg": "Success"
        }
        return build_response(200, user)


def get_user_posts(e):
    """
    Get a paginated list of posts from a given user_id
    """
    PP = e["pathParameters"]
    QSP = e["queryStringParameters"]

    params = {
        "user_id": PP.get("user_id", "error"),
        "offset": QSP.get("offset", "0"),
        "limit": QSP.get("limit", "20"),
    }

    if not valid.get_user_posts.validate(params):
        print(valid.get_user_posts.errors)
        return build_response(400, {"msg": "Error in parameters"})

    user_id = int(params["user_id"])
    offset = int(params["offset"])
    limit = int(params["limit"])
    # Check poster exists
    if not user_exists(user_id):
        return build_response(404, {"msg": "User not found"})

    statement = """
    SELECT post_id,content,p.created_at,username 
    FROM posts p 
    JOIN users u ON p.user_id = u.user_id 
    WHERE p.user_id = %s
    ORDER BY post_id DESC
    OFFSET %s
    LIMIT %s
    """

    cursor.execute(statement, (user_id, offset, limit))
    res = cursor.fetchall()
    posts = []
    for entry in res:
        elapsed = datetime.now(timezone.utc) - entry[2]
        hours_ago = elapsed.days * 24 + elapsed.seconds // 3600
        posts.append(
            {
                "user_id": user_id,
                "post_id": entry[0],
                "content": entry[1],
                "hours_ago": hours_ago,
                "username": entry[3],
                "liked": "N/A",
            }
        )

    return build_response(200, {"msg": "Success", "posts": posts})


def validate_user(e):
    """
    Check a password against a username
    """
    BODY = e["body"]
    if not BODY:
        return build_response(400, {"msg": "No body"})

    if not valid.validate_user.validate(BODY):
        print("error:", valid.validate_user.errors)
        return build_response(400, {"msg": "Error in body"})

    user = BODY["username"]
    guess = BODY["guess"]

    # Check that user exists
    get_user_statement = "SELECT password_hash,user_id FROM users WHERE username = %s"
    cursor.execute(get_user_statement, (user,))
    found = cursor.fetchone()
    if not found:
        return build_response(404, {"msg": "Username not found"})

    # Check password
    stored_hash = found[0]
    storedb64 = base64.b64decode(stored_hash)
    salt, stored_password_hash = storedb64[:16], storedb64[16:]
    hashed_password = hashlib.pbkdf2_hmac("sha256", guess.encode("utf-8"), salt, 10000)
    # Hash input and compare to hash
    if hashed_password == stored_password_hash:
        obj = {"user_id": found[1], "message": "Successful login"}
        return build_response(200, obj)
    else:
        return build_response(401, {"msg": "Invalid Credentials"})

def delete_user(e):
    PP = e['pathParameters']
    
    if not valid.delete_user.validate(PP):
        print(valid.delete_user.errors)
        return build_response(400, {"msg": "Error in body"})

    user_id = int(PP['user_id'])

    if not user_exists(user_id):
        return build_response(400, 'User not found')
    
    statement = "DELETE FROM users WHERE user_id = %s"

    cursor.execute(statement,(user_id,))
    conn.commit()
    return build_response(200, "Successfully deleted")


def get_post(e):
    """
    Get a post from post_id
    """
    params = e["pathParameters"]
    QSP = e["queryStringParameters"]

    if "user" in QSP:
        params["user_id"] = QSP["user"]

    if not valid.get_post.validate(params):
        print("error:", valid.get_post.errors)
        return build_response(400, {"msg": "Error in params"})

    post_id = int(params["post_id"])
    # Make sure post exists
    if not post_exists(post_id):
        return build_response(400, {"msg": "Post not found"})

    if "userid" in params:
        """Implement Likes"""
    else:
        statement = """
        SELECT users.user_id,username,content,posts.created_at 
        FROM posts JOIN users ON posts.user_id = users.user_id 
        WHERE post_id = %s
        """
        cursor.execute(statement, (post_id,))
        res = cursor.fetchone()

        elapsed = datetime.now(timezone.utc) - res[3]
        hours_ago = elapsed.days * 24 + elapsed.seconds // 3600

        obj = {
            "message": "Success",
            "user_id": res[0],
            "username": res[1],
            "content": res[2],
            "hours_ago": hours_ago,
            "liked": "N/A",
        }
        return build_response(200, obj)


def create_post(e):
    """
    Create a post from a user
    """
    BODY = e["body"]

    if not valid.create_post.validate(BODY):
        print("error:", valid.create_post.errors)
        return build_response(400, {"msg": "Error in body"})

    user_id = BODY["user_id"]
    content = BODY["content"]
    # Check poster exists
    if not user_exists(user_id):
        return build_response(400, {"msg": "Poster does not exist"})

    statement = "INSERT INTO posts (user_id,content) VALUES(%s,%s) RETURNING post_id"
    cursor.execute(statement, (user_id, content))
    conn.commit()
    new_id = cursor.fetchone()[0]

    return build_response(200, {"msg": "Created post", "post_id": new_id})


def follow(e):
    """
    Follow between 2 users
    """
    BODY = e["body"]
    if not valid.follow.validate(BODY):
        print(valid.follow.errors)
        return build_response(400, {"msg": "Error in body"})

    follower_id = BODY["follower_id"]
    followee_id = BODY["followee_id"]
    # Cannot self-follow
    if follower_id == followee_id:
        return build_response(400, {"msg": "Cannot have same follower and followee"})
    # Check doesn't exist
    if follow_exists(follower_id, followee_id):
        return build_response(400, {"msg": "Relationship already exists"})
    # Check users exist
    if not user_exists(followee_id) or not user_exists(follower_id):
        return build_response(404, {"msg": "One user does not exist"})

    statement = "INSERT INTO follows (follower_id,followee_id) VALUES(%s,%s)"
    cursor.execute(statement, (follower_id, followee_id))
    conn.commit()
    return build_response(200, {"msg": "Success"})


def unfollow(e):
    """
    Remove follow between 2 users
    """
    BODY = e["body"]

    if not valid.unfollow.validate(BODY):
        print(valid.unfollow.errors)
        return build_response(400, {"msg": "Error in body"})

    unfollower_id = BODY["unfollower_id"]
    unfollowee_id = BODY["unfollowee_id"]
    # Check different
    if unfollower_id == unfollowee_id:
        return build_response(400, {"msg": "Cannot have same follower and followee"})
    # Follow must exist
    if not follow_exists(unfollower_id, unfollowee_id):
        return build_response(404, {"msg": "Relationship doesn't exist"})
    # Users must exist
    if not user_exists(unfollowee_id) or not user_exists(unfollower_id):
        return build_response(404, {"msg": "One user does not exist"})

    statement = "DELETE FROM follows WHERE follower_id = %s AND followee_id = %s"
    cursor.execute(statement, (unfollower_id, unfollowee_id))
    conn.commit()
    return build_response(200, {"msg": "Success"})


def get_comments(e):
    """
    Get paginated comments from a post
    """
    PP = e["pathParameters"]
    QSP = e["queryStringParameters"]
    params = {
        "post_id": PP.get("post_id", "error"),
        "limit": QSP.get("limit", "20"),
        "offset": QSP.get("offset", "0"),
    }

    if not valid.get_comments.validate(params):
        print(valid.get_comments.errors)
        return build_response(400, {"msg": "Error in Parameters"})

    post_id = int(params["post_id"])
    limit = int(params["limit"])
    offset = int(params["offset"])

    if not post_exists(post_id):
        return build_response(404, {"msg": "Post does not exist"})

    statement = """
    SELECT u.user_id,username,c.content,c.created_at
    FROM comments c 
    JOIN posts p ON c.post_id = p.post_id
    JOIN users u ON p.user_id = u.user_id
    WHERE c.post_id = %s
    ORDER BY c.comment_id DESC
    OFFSET %s
    LIMIT %s;
    """

    cursor.execute(statement, (post_id, offset, limit))
    res = cursor.fetchall()
    comments = []

    for entry in res:
        elapsed = datetime.now(timezone.utc) - entry[3]
        hours_ago = elapsed.days * 24 + elapsed.seconds // 3600
        comments.append(
            {
                "user_id": entry[0],
                "username": entry[1],
                "content": entry[2],
                "hours_ago": hours_ago,
            }
        )

    return build_response(200, {"msg": "Success", "comments": comments})


def post_comment(e):
    """
    Comment on a post
    """
    BODY = e["body"]
    PP = e["pathParameters"]
    params = {
        "post_id": PP.get("post_id", "error"),
        "user_id": BODY.get("user_id"),
        "content": BODY.get("content"),
    }

    if not valid.post_comment.validate(params):
        print(valid.post_comment.errors)
        return build_response(400, {"msg": "Error in Params"})

    user_id = params["user_id"]
    post_id = params["post_id"]
    content = params["content"]
    # Check user exists
    if not user_exists(user_id):
        return build_response(404, {"msg": "User does not exist"})
    # Check post exists
    if not post_exists(post_id):
        return build_response(404, {"msg": "Post does not exist"})

    statement = "INSERT INTO comments (user_id,post_id,content) VALUES (%s,%s,%s)"

    cursor.execute(statement, (user_id, post_id, content))
    conn.commit()

    return build_response(200, {"msg": "Success"})


def get_feed_new(e):
    """
    Get paginated list of posts from newest
    """
    QSP = e["queryStringParameters"]
    params = {"limit": QSP.get("limit", 20), "offset": QSP.get("offset", 0)}
    if "user" in QSP:
        params["user"] = QSP["user"]

    if not valid.get_feed.validate(params):
        print(valid.get_feed.errors)
        return build_response(400, {"msg": "Error in params"})

    limit = params["limit"]
    offset = params["offset"]

    if 0:  #'user' in QSP:
        statement = """
        Implement when I implement likes
        """
    else:
        statement = """
        SELECT post_id, username, u.user_id, content, p.created_at
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        ORDER BY post_id DESC
        LIMIT %s
        OFFSET %s
        """
        cursor.execute(statement, (limit, offset))
        res = cursor.fetchall()
        posts = []
        for entry in res:
            elapsed = datetime.now(timezone.utc) - entry[4]
            hours_ago = elapsed.days * 24 + elapsed.seconds // 3600
            posts.append(
                {
                    "user_id": entry[2],
                    "post_id": entry[0],
                    "content": entry[3],
                    "hours_ago": hours_ago,
                    "username": entry[1],
                }
            )
        return build_response(200, {"msg": "Success", "posts": posts})


def get_feed_followed(e):
    """
    Get paginated list of newest posts from accounts that user follows
    """
    QSP = e["queryStringParameters"]
    PP = e["pathParameters"]
    params = {
        "limit": QSP.get("limit", 20),
        "offset": QSP.get("offset", 0),
        "user": PP.get("user_id", "error"),
    }

    if not valid.get_feed.validate(params):
        print(valid.get_feed.errors)
        return build_response(400, {"msg": "Error in params"})
    
    limit = params["limit"]
    offset = params["offset"]
    user_id = params["user"]

    if not user_exists(user_id):
        return build_response(404, {"msg": "User not found"})

    statement = """
    SELECT post_id, username, u.user_id, content, p.created_at
    FROM posts p
    JOIN follows f ON f.followee_id = p.user_id
    JOIN users u ON u.user_id = p.user_id
    WHERE follower_id = %s
    ORDER BY post_id DESC
    LIMIT %s
    OFFSET %s
    """
    cursor.execute(statement, (user_id, limit, offset))
    res = cursor.fetchall()
    posts = []
    for entry in res:
        elapsed = datetime.now(timezone.utc) - entry[4]
        hours_ago = elapsed.days * 24 + elapsed.seconds // 3600
        posts.append(
            {
                "user_id": entry[2],
                "post_id": entry[0],
                "content": entry[3],
                "hours_ago": hours_ago,
                "username": entry[1],
                "liked": "N/A",
            }
        )
    return build_response(200, {"msg": "Success", "posts": posts})


def get_user_followers(e):
    """
    Get paginated list of a users followers
    """
    QSP = e["queryStringParameters"]
    PP = e["pathParameters"]
    params = {
        "limit": QSP.get("limit", 30),
        "offset": QSP.get("offset", 0),
        "user_id": PP.get("user_id", "error"),
    }

    if not valid.get_user_follows.validate(params):
        print(valid.get_user_follows.errors)
        return build_response(400, {"msg": "Error in params"})

    limit = params["limit"]
    offset = params["offset"]
    user_id = int(params["user_id"])
    # Check user exists
    if not user_exists(user_id):
        return build_response(404, {"msg": "User does not exist"})

    statement = """
    SELECT username, user_id
    FROM follows
    JOIN users ON follower_id = user_id
    WHERE followee_id = %s
    ORDER BY follow_id DESC
    LIMIT %s
    OFFSET %s
    """
    cursor.execute(statement, (user_id, limit, offset))
    res = cursor.fetchall()
    followers = []
    for entry in res:
        followers.append({"user_id": entry[1], "username": entry[0]})
    return build_response(200, {"msg": "Success", "followers": followers})


def get_user_following(e):
    """
    Get a paginated list of who a user is following
    """
    QSP = e["queryStringParameters"]
    PP = e["pathParameters"]
    params = {
        "limit": QSP.get("limit", 30),
        "offset": QSP.get("offset", 0),
        "user_id": PP.get("user_id", "error"),
    }

    if not valid.get_user_follows.validate(params):
        print(valid.get_user_follows.errors)
        return build_response(400, {"msg": "Error in params"})

    limit = params["limit"]
    offset = params["offset"]
    user_id = int(params["user_id"])
    # Check user exists
    if not user_exists(user_id):
        return build_response(400, {"msg": "User does not exist"})

    statement = """
    SELECT username, user_id
    FROM follows
    JOIN users ON follower_id = user_id
    WHERE follower_id = %s
    ORDER BY follow_id DESC
    LIMIT %s
    OFFSET %s
    """
    cursor.execute(statement, (user_id, limit, offset))
    res = cursor.fetchall()
    following = []
    for entry in res:
        following.append({"user_id": entry[1], "username": entry[0]})
    return build_response(200, {"msg": "Success", "followers": following})


# see if user exists
def user_exists(user_id):
    statement = "SELECT username FROM users WHERE user_id = %s"
    cursor.execute(statement, (user_id,))
    check = cursor.fetchone()
    if check is None:
        return False
    else:
        return True


# see if post exists
def post_exists(post_id):
    statement = "SELECT * FROM posts WHERE post_id = %s"
    cursor.execute(statement, (post_id,))
    check = cursor.fetchone()
    if check is None:
        return False
    else:
        return True


# see if follow exists
def follow_exists(follower_id, followee_id):
    statement = "SELECT * FROM follows WHERE follower_id = %s AND followee_id = %s"
    cursor.execute(statement, (follower_id, followee_id))

    res = cursor.fetchone()
    if res is None:
        return False
    else:
        return True


# See if like exists
def like_exists(post_id, user_id):
    raise NotImplementedError

# Return json object with code and body
def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


#print(lambda_handler(mock.create_user_event,None))
#print(lambda_handler(mock.get_user_event,None))
#print(lambda_handler(mock.validate_user_event_bad,None))
#print(lambda_handler(mock.validate_user_event_good,None))
#print(lambda_handler(mock.create_post_event,None))
#print(lambda_handler(mock.get_post_event,None))
#print(lambda_handler(mock.follow_event,None))
#print(lambda_handler(mock.unfollow_event,None))
#print(lambda_handler(mock.get_comments_event,None))
#print(lambda_handler(mock.post_comment_event,None))
#print(lambda_handler(mock.get_user_posts_event,None))
#print(lambda_handler(mock.get_followers_event,None))
#print(lambda_handler(mock.get_following_event,None))
#print(lambda_handler(mock.get_new_feed_event,None))
print(lambda_handler(mock.get_followed_feed_event,None))
#print(lambda_handler(mock.delete_user_event,None))



# GOALS

# Delete user
# Delete post
# Patch email,username,phone number
# Implement post likes
# Feed by likes
# Hashtags in future?
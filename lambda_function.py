import os,json,psycopg2,dotenv,hashlib,base64,time
from datetime import datetime,timezone
import data_validators as valid
from testevents import *
from dotenv import load_dotenv
load_dotenv()

"""
Main API code for all endpoints, may split into more files at some point
"""
start_time = time.time()
db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_port = os.environ['DB_PORT']


get_user_by_username = "/users/username"
user_create = "/users/create"
user_auth = "/users/auth"

get_post_by_id = '/posts/id'
post_create = '/posts/create'

follow_path = '/relationships/follow'
unfollow_path = '/relationships/unfollow'

comment_on = '/posts/comment'



conn = psycopg2.connect(
    host=db_host,
    dbname=db_name,
    user=db_user,
    password=db_password,
    port=db_port
)
cursor = conn.cursor()

def lambda_handler(event,context):
    
    method = event.get('httpMethod')
    path = event.get('path')

    if 'queryStringParameters' not in event:
        event['queryStringParameters'] = {}
    if 'body' not in event:
        event['body'] = {}
    if 'pathParameters' not in event:
        event['pathParameters'] = {}

    # Try to implement handlers for each path maybe

    try: #
        if path.startswith('/users'):
            if path.startswith(get_user_by_username) and method == 'GET':
                return get_user(event)
            elif path == user_create and method == 'POST':
                return create_user(event)
            elif path == user_auth and method == 'POST':
                return validate_user(event)
            
        elif path.startswith('/posts'):
            if path.startswith(get_post_by_id) and method == 'GET':
                return get_post(event)
            elif path == post_create and method == 'POST':
                return create_post(event)
            elif path == comment_on and method == 'POST':
                return post_comment(event)
            else:
                splits = path.split('/')
                if len(splits)>3 and splits[3] == 'comments':
                    return get_comments(event)
        
        elif path.startswith('/relationships'):
            if path == follow_path and method == 'POST':
                return follow(event)
            elif path == unfollow_path and method == 'POST':
                return unfollow(event)

        return build_response(400,{"msg":"Not implemented for this endpoint"})
        
    except NotImplementedError: #This is just so I see the actual errors while developing. Exception as e:
        return build_response(500,{"msg": type("e").__name__})
    
    finally:
        cursor.close()
        conn.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Took {elapsed_time:.4f} seconds to execute.")

def create_user(e):
    BODY = e['body']

    if not valid.create_user(BODY):
        print("error:",valid.create_user.errors) # remove these later
        return build_response(400,{"msg": "Error in body"})
    
    password = BODY['password']
    username = BODY['username']
    
    statement = 'SELECT * FROM users WHERE username = %s'
    cursor.execute(statement,(username,))
    check = cursor.fetchone()
    if check:
        return build_response(400,{"msg": "Username is taken"})

    # Encode password by creating salt
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)
    hash = base64.b64encode(salt+hashed_password).decode('utf-8')

    statement = "INSERT INTO users (username,password_hash) VALUES(%s,%s) RETURNING user_id"
    cursor.execute(statement,(username,hash))
    conn.commit()
    new_id = cursor.fetchone()[0]
    
    return build_response(200,{"msg": "Sucessfully added","new_user_id":new_id})

def get_user(e):

    params = e['pathParameters']

    if not valid.get_user.validate(params):
        print("error:",valid.get_user.errors)
        return build_response(400,{"msg": "Error in parameters"})
    
    username = params['username']

    statement = "SELECT user_id FROM users WHERE username = %s"

    cursor.execute(statement,(username,))
    res = cursor.fetchone()
    
    if res is None:
        return build_response(404,{"msg": "User does not exist"})

    statement = "I need to look up subqueries"

    obj = {'username': username, 'user_id': res[0], 'followers': 0,'following':0,'msg': "Success"}
    return build_response(200,obj)

def validate_user(e):
    BODY = e['body']
    if not BODY:
        return build_response(400,{"msg": "No body"})

    if not valid.validate_user.validate(BODY):
        print("error:",valid.validate_user.errors)
        return build_response(400,{"msg": "Error in body"})

    user = BODY['username']
    guess = BODY['guess']
    
    # check that user exists
    get_user_statement = 'SELECT password_hash,user_id FROM users WHERE username = %s'
    cursor.execute(get_user_statement,(user,))
    found = cursor.fetchone()
    if not found:
        return build_response(400,{"msg": "Invalid credentials"})

    # check password
    stored_hash = found[0]
    storedb64 = base64.b64decode(stored_hash)
    salt,stored_password_hash = storedb64[:16],storedb64[16:]
    hashed_password = hashlib.pbkdf2_hmac('sha256', guess.encode('utf-8'), salt, 10000)  # hash input

    if hashed_password == stored_password_hash:
        obj = {'user_id': found[1],'message': "Success"}
        return build_response(200,obj)
    else:
        return build_response(400,{"msg": "Invalid Credentials"})

def get_post(e):
    params = e['pathParameters']

    if not valid.get_post.validate(params):
        print("error:",valid.get_post.errors)
        return build_response(400,{"msg": "Error in params"})
    
    post_id = int(params['post_id'])

    statement = "SELECT users.user_id,username,content,posts.created_at FROM posts JOIN users ON posts.user_id = users.user_id WHERE post_id = %s"
    cursor.execute(statement,(post_id,))
    res = cursor.fetchone()
    if res is None:
        return build_response(404,{'msg':'Post not found'})
    
    elapsed = (datetime.now(timezone.utc)-res[3])
    hours_ago = elapsed.days*24 + elapsed.seconds//3600

    obj = {'message':'Success','poster_id': res[0],'poster_name': res[1], 'content': res[2], 'hours_ago': hours_ago}
    return build_response(200,obj)


def create_post(e):
    BODY = e['body']
    
    if not valid.create_post.validate(BODY):
        print("error:",valid.create_post.errors)
        return build_response(400,{"msg": "Error in body"})

    user_id = BODY['user_id']
    content = BODY['content']

    # check that user exists
    if not user_exists(user_id):
        return build_response(400,{"msg": "Poster does not exist"})
    
    statement = "INSERT INTO posts (user_id,content) VALUES(%s,%s) RETURNING post_id"
    cursor.execute(statement,(user_id,content))
    conn.commit()
    new_id = cursor.fetchone()[0]

    return build_response(200,{"msg": "Created post","post_id": new_id})


def follow(e):
    BODY = e['body']

    if not valid.follow.validate(BODY):
        print(valid.follow.errors)
        return build_response(400,{"msg": "Error in body"})
    
    follower_id = BODY['follower_id']
    followee_id = BODY['followee_id']

    if follow_exists(follower_id,followee_id):
        return build_response(400,{"msg": "Relationship already exists"})

    if not user_exists(followee_id) or not user_exists(follower_id):
        return build_response(400,{"msg": "One user does not exist"})

    statement = "INSERT INTO follows (follower_id,followee_id) VALUES(%s,%s)"
    cursor.execute(statement,(follower_id,followee_id))
    conn.commit()
    return build_response(200,{'msg':'Success'})

def unfollow(e):
    BODY = e['body']
    
    if not valid.unfollow.validate(BODY):
        print(valid.unfollow.errors)
        return build_response(400,{"msg": "Error in body"})
    
    unfollower_id = BODY['unfollower_id']
    unfollowee_id = BODY['unfollowee_id']

    if not follow_exists(unfollower_id,unfollowee_id):
        return build_response(400,{"msg": "Relationship doesn't exists"})

    if not user_exists(unfollowee_id) or not user_exists(unfollower_id):
        return build_response(400,{"msg": "One user does not exist"})
    
    statement = "DELETE FROM follows WHERE follower_id = %s AND followee_id = %s"
    cursor.execute(statement,(unfollower_id,unfollowee_id))
    conn.commit()
    return build_response(200,{'msg':'Success'})

def get_comments(e):

    PP = e['pathParameters']
    QSP = e['queryStringParameters']
    params = {'post_id': PP.get('post_id',"error"),'limit':QSP.get('limit',"20"),'offset':QSP.get('offset',"0")}

    if not valid.get_comments.validate(params):
        print(valid.get_comments.errors)
        return build_response(400,{'msg':'Error in Parameters'})
    
    post_id = int(params['post_id'])

    statement = """
    SELECT u.user_id,username,c.content,c.created_at
    FROM comments c 
    JOIN posts p ON c.post_id = p.post_id
    JOIN users u ON p.user_id = u.user_id
    WHERE c.post_id = %s;
    """

    cursor.execute(statement,(post_id,))
    res = cursor.fetchall()
    comments = []

    for entry in res:
        elapsed = (datetime.now(timezone.utc)-entry[3])
        hours_ago = elapsed.days*24 + elapsed.seconds//3600
        comments.append({'user_id':entry[0],'username':entry[1],'content':entry[2],'hours_ago':hours_ago})

    return build_response(200,{'msg':"Success","comments":comments})

def post_comment(e):
    BODY = e['body']
    
    if not valid.post_comment.validate(BODY):
        print(valid.post_comment.errors)
        return build_response(400,{'msg':'Error in Body'})
    
    user_id = BODY['user_id']
    post_id = BODY['post_id']
    content = BODY['content']

    if not user_exists(user_id):
        return build_response(400,{'msg':'User does not exist'})
    
    if not post_exists(post_id):
        return build_response(400,{'msg':'Post does not exist'})

    statement = "INSERT INTO comments (user_id,post_id,content) VALUES (%s,%s,%s)"

    cursor.execute(statement,(user_id,post_id,content))
    conn.commit()

    return build_response(400,{'msg':"Success"})


# see if user exists
def user_exists(user_id):
    statement = "SELECT username FROM users WHERE user_id = %s"
    cursor.execute(statement,(user_id,))
    check = cursor.fetchone()
    if check is None:
        return False
    else:
        return True

# see if post exists
def post_exists(post_id):
    statement = "SELECT * FROM posts WHERE post_id = %s"
    cursor.execute(statement,(post_id,))
    check = cursor.fetchone()
    if check is None:
        return False
    else:
        return True

# see if follow exists
def follow_exists(follower_id,followee_id):
    statement = "SELECT * FROM follows WHERE follower_id = %s AND followee_id = %s"
    cursor.execute(statement,(follower_id,followee_id))

    res = cursor.fetchone()
    if res is None:
        return False
    else:
        return True

# Return json object with code and body
def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }



#print(lambda_handler(create_user_event,None))
#print(lambda_handler(get_user_event,None))
#print(lambda_handler(validate_user_event_bad,None))
#print(lambda_handler(validate_user_event_good,None))
#print(lambda_handler(create_post_event,None))
#print(lambda_handler(get_post_event,None))
#print(lambda_handler(follow_event,None))
#print(lambda_handler(unfollow_event,None))
#print(lambda_handler(get_comments_event,None))
#print(lambda_handler(post_comment_event,None))

# TODAY GOALS
# Implement: comment on post | Done
# Get follower count, following count
# Get posts by user
# 2+ days
# Implement post likes
# Query by likes

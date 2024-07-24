import os,json,pg8000,datetime,dotenv,hashlib,base64,time
import data_validators as valid
from testevents import *
from dotenv import load_dotenv
load_dotenv()

"""
Main API code for all endpoints, may split into more files at some point
"""

db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_port = os.environ['DB_PORT']


user_path = "/user"
user_auth = "/user/auth"
post_path = '/post'
follow_path = '/relationships/follow'
unfollow_path = '/relationships/unfollow'
comment_path = '/post/comment'


conn = pg8000.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password,
    port=db_port
)
cursor = conn.cursor()

def timer_wrapper(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Took {elapsed_time:.4f} seconds to execute.")
        return result
    return wrapper

@timer_wrapper # will remove eventually
def lambda_handler(event,context):
    
    method = event.get('httpMethod')
    path = event.get('path')
    # Try to implement handlers for each path maybe

    try: # clean up sometime
        if path == user_path and method == 'POST':
            return create_user(event)
        elif path == user_path and method == 'GET':
            return get_user(event)
        elif path == user_auth and method == 'GET':
            return validate_user(event)
        elif path == post_path and method == 'GET':
            return get_post(event)
        elif path == post_path and method == 'POST':
            return create_post(event)
        elif path == follow_path and method == 'POST':
            return follow(event)
        elif path == unfollow_path and method == 'POST':
            return unfollow(event)
        elif path == comment_path and method == 'GET':
            return get_comments(event)
        elif path == comment_path and method == 'POST':
            return post_comment(event)
        else:
            return build_response(400,{"msg":"Not implemented for this endpoint"})
        
    except NotImplementedError: #This is just so I see the actual errors while developing. Exception as e:
        return build_response(500,{"msg": type("e").__name__})
    
    finally:
        cursor.close()
        conn.close()

def create_user(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,{"msg": "No body"})

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
    QSP = e.get('queryStringParameters')
    if not QSP:
        return build_response(400,{"msg": "No QSP"})

    if not valid.get_user.validate(QSP):
        print("error:",valid.get_user.errors)
        return build_response(400,{"msg": "Error in QSP"})
    
    username = QSP.get('user')

    statement = "SELECT user_id FROM users WHERE username = %s"

    cursor.execute(statement,(username,))
    res = cursor.fetchone()
    
    if res is None:
        return build_response(404,{"msg": "User does not exist"})

    statement = "I need to look up subqueries"

    obj = {'username': username, 'user_id': res[0], 'followers': 0,'following':0,'msg': "Success"}
    return build_response(200,obj)

def validate_user(e):
    BODY = e.get('body')
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
    QSP = e.get('queryStringParameters')
    if not QSP:
        return build_response(400,{"msg": "No QSP"})

    if not valid.get_post.validate(QSP):
        print("error:",valid.get_post.errors)
        return build_response(400,{"msg": "Error in QSP"})
    
    post_id = int(QSP['post_id'])

    statement = "SELECT users.user_id,username,content FROM posts JOIN users ON posts.user_id = users.user_id WHERE post_id = %s"
    cursor.execute(statement,(post_id,))
    res = cursor.fetchone()
    if res is None:
        return build_response(404,{'msg':'Post not found'})
    
    obj = {'message':'Success','poster_id': res[0],'poster_name': res[1], 'content': res[2]}
    return build_response(200,obj)


def create_post(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,{"msg": "No body"})
    
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
    BODY = e.get('body')
    if not BODY:
        return build_response(400,{"msg": "No body"})
    
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
    BODY = e.get('body')
    if not BODY:
        return build_response(400,{"msg": "No body"})
    
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
    QSP = e.get('queryStringParameters')
    if QSP is None:
        return build_response(400,{'msg':'NO QSP'})
    
    if not valid.get_comments.validate(QSP):
        print(valid.get_comments.errors)
        return build_response(400,{'msg':'Error in QSP'})
    
    return build_response(400,{'msg':"Good so far"})

def post_comment(e):
    BODY = e.get('body')
    if BODY is None:
        return build_response(400,{'msg':'NO QSP'})
    
    if not valid.post_comment.validate(BODY):
        print(valid.post_comment.errors)
        return build_response(400,{'msg':'Error in Body'})
    
    return build_response(400,{'msg':"Good so far"})


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
    statement = "SELECT * FROM post WHERE post_id = %s"
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
print(lambda_handler(post_comment_event,None))

# TODAY GOALS
# Implement: comment on post, get posts by followed user
# Get follower count, following count
# 2+ days
# Implement post likes
# Query by likes

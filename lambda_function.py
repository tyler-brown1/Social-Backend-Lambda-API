import os,json,pg8000,datetime,dotenv,hashlib,base64
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
follow_path = '/follow'


conn = pg8000.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password,
    port=db_port
)
cursor = conn.cursor()

def lambda_handler(event,context):
    
    method = event.get('httpMethod')
    path = event.get('path')
    # Try to implement handlers for each path maybe

    try:
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
        else:
            return build_response(400,"Not implemented for this endpoint")
        
    except NotImplementedError: #This is just so I see the actual errors while developing. Exception as e:
        return build_response(500,type("e").__name__)
    
    finally:
        cursor.close()
        conn.close()

def create_user(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,"No Body")

    if not valid.create_user(BODY):
        print("error:",valid.create_user.errors) # remove these later
        return build_response(400,"Error in body")
    
    password = BODY['password']
    username = BODY['username']
    
    statement = 'SELECT * FROM users WHERE username = %s'
    cursor.execute(statement,(username,))
    check = cursor.fetchone()
    if check:
        return build_response(400,"Username is taken")

    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)
    hash = base64.b64encode(salt+hashed_password).decode('utf-8')
    statement = "INSERT INTO users (username,password_hash) VALUES(%s,%s)"
    cursor.execute(statement,(username,hash))
    conn.commit()
    
    return build_response(200,'Successfully added!')

def get_user(e):
    QSP = e.get('queryStringParameters')
    if not QSP:
        return build_response(400,"No Query String Parameters")

    if not valid.get_user(QSP):
        print("error:",valid.get_user.errors)
        return build_response(400,"Error in body")
    
    username = QSP.get('user')

    statement = "SELECT user_id FROM users WHERE username = %s;"
    cursor.execute(statement,(username,))
    res = cursor.fetchone()
    
    if res is None:
        return build_response(404,"User does not exist")

    obj = {'username': username, 'user_id': res[0]}
    return build_response(200,obj)

def validate_user(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,"No Body")

    if not valid.validate_user(BODY):
        print("error:",valid.validate_user.errors)
        return build_response(400,"Error in body")

    user = BODY['username']
    guess = BODY['guess']
    
    # check that user exists
    get_user_statement = 'SELECT password_hash,user_id FROM users WHERE username = %s'
    cursor.execute(get_user_statement,(user,))
    found = cursor.fetchone()
    if not found:
        return build_response(400,'Invalid credentials')

    # check password
    stored_hash = found[0]
    storedb64 = base64.b64decode(stored_hash)
    salt,stored_password_hash = storedb64[:16],storedb64[16:]
    hashed_password = hashlib.pbkdf2_hmac('sha256', guess.encode('utf-8'), salt, 10000)  # hash input

    if hashed_password == stored_password_hash:
        obj = {'user_id': found[1]}
        return build_response(200,obj)
    else:
        return build_response(400,'Invalid credentials')

def get_post(e):
    QSP = e.get('queryStringParameters')
    if not QSP:
        return build_response(400, 'No Query Strings')

    if not valid.get_post(QSP):
        print("error:",valid.get_post.errors)
        return build_response(400,"Error in QSP")
    
    post_id = QSP['post_id']

    statement = "SELECT users.user_id,username,content FROM posts JOIN users ON posts.user_id = users.user_id WHERE post_id = %s"
    cursor.execute(statement,(post_id,))
    res = cursor.fetchone()
    if res is None:
        return build_response(404,'Post not found')
    # get comments later
    obj = {'poster_id': res[0],'poster_name': res[1], 'content': res[2], 'comments': ['not implemented']}
    return build_response(obj,obj)


def create_post(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,'No body')
    
    if not valid.create_post(BODY):
        print("error:",valid.create_post.errors)
        return build_response(400,"Error in body")

    user_id = BODY['user_id']
    content = BODY['content']

    # check that user exists
    if not user_exists(user_id):
        return build_response(400,"Poster does not exist")
    
    statement = "INSERT INTO posts (user_id,content) VALUES(%s,%s)"
    cursor.execute(statement,(user_id,content))
    conn.commit()

    return build_response(200,"Created post")


def follow(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,"No body")
    
    if not valid.follow.validate(BODY):
        return build_response(400,"Missing parameter")
    
    follower_id = BODY['follower_id']
    followee_id = BODY['followee_id']

    if not user_exists(followee_id) or not user_exists(follower_id):
        return build_response(400,'One user does not exist')

    return build_response(200,"Good so far")

# see if user exists
def user_exists(user_id):
    statement = "SELECT username FROM users WHERE user_id = %s"
    cursor.execute(statement,(user_id,))
    check = cursor.fetchone()
    if check is None:
        return False
    else:
        return True

# post_exists function also implement

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

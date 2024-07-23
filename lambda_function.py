import os,json,pg8000,datetime,dotenv,hashlib,base64
import data_validators as valid
from testevents import *
from dotenv import load_dotenv
load_dotenv()

db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_port = os.environ['DB_PORT']


user_path = "/user"
user_auth = "/user/auth"
post_path = '/post'


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
        else:
            return build_response(400,(method,path))
    except NotImplementedError: #Exception as e:
        return build_response(500,type("e").__name__)
    
    finally:
        cursor.close()
        conn.close()

def create_user(e):
    ### NEED TO IMPLEMENT CHECK USER IS UNIQUE FIRST
    BODY = e.get('body')
    if not BODY:
        return build_response(400,"No Body")
    

    if not valid.create_user(BODY):
        print("error:",valid.create_user.errors) # remove these later
        return build_response(400,"Error in body")
    
    password = BODY['password']
    username = BODY['username']
    
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
        print("error:",valid.create_user.errors)
        return build_response(400,"Error in body")
    
    username = QSP.get('username')

    statement = "SELECT user_id,username FROM users WHERE username = %s;"
    cursor.execute(statement,(username,))
    res = cursor.fetchone()
    
    if not res:
        return build_response(400,"User does not exist")

    return build_response(200,res)

def validate_user(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,"No body")
    user = BODY.get('username')
    guess = BODY.get('input')
    if None in [user,guess]:
        return build_response(400,"Invalid Body Parameters")
    
    get_user_statement = 'SELECT password_hash FROM USERS WHERE username = %s'
    cursor.execute(get_user_statement,(user,))
    found = cursor.fetchone()
    if not found:
        print('user not found')
        return build_response(400,'Invalid credentials')

    stored_hash = found[0]
    storedb64 = base64.b64decode(stored_hash)
    salt,stored_password_hash = storedb64[:16],storedb64[16:]
    hashed_password = hashlib.pbkdf2_hmac('sha256', guess.encode('utf-8'), salt, 10000)  # hash input

    if hashed_password == stored_password_hash:
        return build_response(200,'Correct credentials')
    else:
        return build_response(400,'Invalid credentials')

def get_post(e):
    raise NotImplementedError

def create_post(e):
    BODY = e.get('body')
    if not BODY:
        return build_response(400,'No body')
    
    user_id = e.get('user_id')
    content = e.get('content')
    if None in [user_id, content]:
        return build_response(400,'Parameter missing')
    image_url = e.get('image_url')

    if image_url is None:
        statement = "INSERT INTO users (user_id,content) VALUES(%s,%s)"
    else:
        statement = "INSERT INTO users (user_id,content,image_url) VALUES(%s,%s,%s)"

    # not finished
    

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }


#print(lambda_handler(post_user_event,None))
print(lambda_handler(get_user_event,None))
#print(lambda_handler(validate_user_event_bad,None))
#print(lambda_handler(validate_user_event_good,None))
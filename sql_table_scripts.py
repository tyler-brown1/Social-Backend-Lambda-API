import os,pg8000,random
from dotenv import load_dotenv
load_dotenv()

"""
Some Scripts if I want to drop/populate/update schema in tables
"""

db_host = os.environ['DB_HOST']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_port = os.environ['DB_PORT']

conn = pg8000.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password,
    port=db_port
)
cursor = conn.cursor()  

def create_tables():
    users_create = """
    CREATE TABLE users(
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(12) UNIQUE NOT NULL,
        password_hash VARCHAR(64) NOT NULL
    )"""
    posts_create = """
    CREATE TABLE posts(
        post_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        content VARCHAR(300) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
    )"""
    follows_create = """
    CREATE TABLE follows(
        follower_id INT NOT NULL,
        followee_id INT NOT NULL,
        email VARCHAR(64),
        followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (follower_id, followee_id),
        FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (followee_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """
    comments_create = """
    CREATE TABLE comments(
        comment_id SERIAL PRIMARY KEY,
        post_id INT NOT NULL,
        user_id INT NOT NULL,
        content VARCHAR(300) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
        FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE
    )
    """
    cursor.execute(users_create)
    cursor.execute(posts_create)
    cursor.execute(follows_create)
    cursor.execute(comments_create)
    conn.commit()
    print("Created")


def delete_tables():
    users_delete = "DELETE FROM users"
    posts_delete = "DELETE FROM posts"
    follows_delete = "DELETE FROM follows"
    comments_delete = "DELETE FROM comments"

    cursor.execute(comments_delete)
    cursor.execute(users_delete)
    cursor.execute(posts_delete)
    cursor.execute(follows_delete)
    conn.commit()
    print("Deleted")

def drop_tables():
    users_drop = "DROP TABLE users"
    posts_drop = "DROP TABLE posts"
    follows_drop = "DROP TABLE follows"
    comments_drop = "DROP TABLE comments"

    cursor.execute(comments_drop)
    cursor.execute(follows_drop)
    cursor.execute(posts_drop)
    cursor.execute(users_drop)
    conn.commit()
    print("Dropped tables")

def populate_users():
    users = []
    for i in range(5):
        users.append((f'user{i+1}',"a"))
    statement = "INSERT INTO users (username,password_hash) VALUES(%s,%s)"
    cursor.executemany(statement,users)
    conn.commit()
    print("Added users")

def populate_follows():
    follows = set()
    for i in range(2000):
        a = random.randint(1,100)
        b = random.randint(1,100)
        if (a,b) in follows: continue
        follows.add((a,b))
    statement = "INSERT INTO follows (follower_id,followee_id) VALUES (%s,%s)"
    cursor.executemany(statement,list(follows))
    conn.commit()
    print("Added follows")

def populate_posts():
    posts = []
    for i in range(20):
        a = random.randint(1,5)
        posts.append((a,f'post #{i+1}'))
    statement = "INSERT INTO posts (user_id,content) VALUES (%s,%s)"
    cursor.executemany(statement,posts)
    conn.commit()
    print("Added posts")

drop_tables()
create_tables()
populate_users()
populate_posts()

cursor.close()
conn.close()


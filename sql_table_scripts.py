import os
import psycopg2
import random
from dotenv import load_dotenv

load_dotenv()

"""
Some Scripts if I want to drop/populate/update schema in tables
"""

db_host = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_port = os.environ["DB_PORT"]

conn = psycopg2.connect(
    host=db_host, dbname=db_name, user=db_user, password=db_password, port=db_port
)
cursor = conn.cursor()


def create_tables():
    users_create = """
    CREATE TABLE users(
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(12) UNIQUE NOT NULL,
        password_hash VARCHAR(64) NOT NULL,
        phone_number VARCHAR(16),
        email VARCHAR(64),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )"""
    posts_create = """
    CREATE TABLE posts(
        post_id SERIAL PRIMARY KEY,
        user_id INT,
        content VARCHAR(300) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
    )"""
    follows_create = """
    CREATE TABLE follows(
        follow_id SERIAL PRIMARY KEY,
        follower_id INT NOT NULL,
        followee_id INT NOT NULL,
        followed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (follower_id, followee_id),
        FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (followee_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    """
    comments_create = """
    CREATE TABLE comments(
        comment_id SERIAL PRIMARY KEY,
        post_id INT NOT NULL,
        user_id INT,
        content VARCHAR(300) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
        FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE
    )
    """
    cursor.execute(users_create)
    cursor.execute(posts_create)
    cursor.execute(follows_create)
    cursor.execute(comments_create)
    conn.commit()
    print("Created tables")


def delete_tables():
    users_delete = "DELETE FROM users"
    posts_delete = "DELETE FROM posts"
    follows_delete = "DELETE FROM follows"
    comments_delete = "DELETE FROM comments"

    cursor.execute(comments_delete)
    cursor.execute(users_delete)
    cursor.execute(posts_delete)
    cursor.execute(follows_delete)
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
    print("Dropped tables")


num_users = 30
num_posts = 100
num_follows = 200
num_comments = 100


def populate_users():
    users = []
    for i in range(num_users):
        users.append((f"user{i+1}", "a"))
    statement = "INSERT INTO users (username,password_hash) VALUES(%s,%s)"
    cursor.executemany(statement, users)
    print("Added users")


def populate_follows():
    follows = set()
    for i in range(num_follows):
        a = random.randint(1, num_users)
        b = random.randint(1, num_users)
        if a == b or (a, b) in follows:
            continue
        follows.add((a, b))
    statement = "INSERT INTO follows (follower_id,followee_id) VALUES (%s,%s)"
    cursor.executemany(statement, list(follows))
    print("Added follows")


def populate_posts():
    posts = []
    for i in range(num_posts):
        a = random.randint(1, num_users)
        posts.append((a, f"post #{i+1} by user {a}"))
    statement = "INSERT INTO posts (user_id,content) VALUES (%s,%s)"
    cursor.executemany(statement, posts)
    print("Added posts")


def populate_comments():
    posts = []
    for i in range(num_comments):
        a = random.randint(1, num_users)
        b = random.randint(1, num_posts)
        posts.append((a, f"comment #{i+1} on post {b}", b))
    statement = "INSERT INTO comments (user_id,content,post_id) VALUES (%s,%s,%s)"
    cursor.executemany(statement, posts)
    print("Added comments")


drop_tables()
create_tables()
populate_users()
populate_posts()
populate_follows()
populate_comments()
conn.commit()

cursor.close()
conn.close()

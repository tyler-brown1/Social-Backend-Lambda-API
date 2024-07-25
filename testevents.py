"""
Mock Event objects to test
"""

create_user_event = {
  "httpMethod": "POST",
  "path": "/users/create",
  "body": {
    "username": "bob5",
    "password": "thisIsMyPassword"
  }
}

get_user_event = {
  "httpMethod": "GET",
  "path": "/users/username/user1",
  "pathParameters":{
      "username": "user1a"
  }
}

validate_user_event_bad = {
  "httpMethod": "POST",
  "path": "/users/auth",
  "body": {
    "username": "bob3",
    "guess": "thisIsNotMyPassword"
  }
}

validate_user_event_good = {
  "httpMethod": "POST",
  "path": "/users/auth",
  "body": {
    "username": "bob3",
    "guess": "thisIsMyPassword"
  }
}

create_post_event = {
  "httpMethod": "POST",
  "path": "/posts/create",
  "body": {
    "user_id": 1,
    "content": "First post"
  }
}

get_post_event = {
  "httpMethod": "GET",
  "path": "/posts/id/1",
  "pathParameters": {
    "post_id": "1"
  }
}

follow_event = {
  "httpMethod": "POST",
  "path": "/relationships/follow",
  "body": {
    "follower_id": 2,
    "followee_id": 1
  }
}

unfollow_event = {
  "httpMethod": "POST",
  "path": "/relationships/unfollow",
  "body": {
    "unfollower_id": 1,
    "unfollowee_id": 3
  }
}

post_comment_event = {
  "httpMethod": "POST",
  "path": "/posts/comment",
  "body": {
    "post_id": 2,
    "user_id": 4,
    "content": "Second comment!"
  }
}

get_comments_event = {
  "httpMethod": "GET",
  "path": "/posts/1/comments",
  "queryStringParameters": {
    "limit": "20",
    "offset": "0"
  },
  "pathParameters":{
    "post_id": "2"
  }
}

get_user_posts_event = {
  "httpMethod": "GET",
  "path": "/users/1/posts",
  "queryStringParameters": {
    "limit": "5",
    "offset": "0"
  },
  "pathParameters":{
    "user_id": "2"
  }
}

get_new_feed_event = {
  "httpMethod": "GET",
  "path": "/feed/new",
  "queryStringParameters": {
    "limit": "3", 
    "offset": "1",
    #"user":"1"
  }
}
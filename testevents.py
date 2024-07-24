"""
Mock Event objects to test
"""

create_user_event = {
  "httpMethod": "POST",
  "path": "/user",
  "body": {
    "username": "bob3",
    "password": "thisIsMyPassword"
  }
}

get_user_event = {
  "httpMethod": "GET",
  "path": "/user",
  "queryStringParameters": {
    "user": "bob334",
  }
}

validate_user_event_bad = {
  "httpMethod": "GET",
  "path": "/user/auth",
  "body": {
    "username": "bob334",
    "guess": "thisIsNotMyPassword"
  }
}

validate_user_event_good = {
  "httpMethod": "GET",
  "path": "/user/auth",
  "body": {
    "username": "bob334",
    "guess": "thisIsMyPassword"
  }
}

create_post_event = {
  "httpMethod": "POST",
  "path": "/post",
  "body": {
    "user_id": 1,
    "content": "First post"
  }
}

get_post_event = {
  "httpMethod": "GET",
  "path": "/post",
  "queryStringParameters": {
    "post_id": "1"
  }
}

follow_event = {
  "httpMethod": "POST",
  "path": "/relationships/follow",
  "body": {
    "follower_id": 1,
    "followee_id": 3
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
  "path": "/post/comment",
  "body": {
    "post_id": 1,
    "user_id": 3,
    "content": "First comment"
  }
}

get_comments_event = {
  "httpMethod": "GET",
  "path": "/post/comment",
  "queryStringParameters": {
    "post_id": "1",
    "limit": "20",
    "offset": "0"
  }
}
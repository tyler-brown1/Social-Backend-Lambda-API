"""
Mock Event objects to test
"""

create_user_event = {
  "httpMethod": "POST",
  "path": "/user",
  "body": {
    "username": "bob334",
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
    "user_id": 100,
    "content": "Second post"
  }
}

get_post_event = {
  "httpMethod": "GET",
  "path": "/post",
  "queryStringParameters": {
    "post_id": 3
  }
}

follow_event = {
  "httpMethod": "POST",
  "path": "/follow",
  "body": {
    "follower_id": 1,
    "followee_id": 50
  }
}
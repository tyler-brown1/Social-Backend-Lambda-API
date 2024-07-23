post_user_event = {
  "httpMethod": "POST",
  "path": "/user",
  "body": {
    "username": "bob329",
    "password": "thisIsMyPassword"
  }
}

get_user_event = {
  "httpMethod": "GET",
  "path": "/user",
  "queryStringParameters": {
    "username": "bob327",
  }
}

validate_user_event_bad = {
  "httpMethod": "GET",
  "path": "/user/auth",
  "body": {
    "username": "bob326",
    "input": "thisIsNotMyPassword"
  }
}

validate_user_event_good = {
  "httpMethod": "GET",
  "path": "/user/auth",
  "body": {
    "username": "bob327",
    "input": "thisIsMyPassword"
  }
}
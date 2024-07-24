API DOCUMENTATION
=================

/user:
    GET /user?user=username -> {user_id, username, follower_ct, following_ct <- follows not implemented}
    - Get a users information
    ** 'user':{'type':'string','required':True}

    
    POST /user {username,password}
    - Create a new user
    ** 'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
    ** 'password':{'type':'string','minlength':5,'maxlength':18,'required':True}

    /auth:
        POST /auth {username,password} -> {user_id if valid}
        - See if password is correct for a user
        ** 'username':{'type':'string','required':True},
        ** 'guess' :{'type':'string','required':True}
    
    want to implement: get following list , get followers list

/post:
    GET /post?id=postid -> {poster_name, poster_id, content, comments:[userid,username,content] }
    - Get a post's details and comments
    ** 'post_id':{'type':'int','required':True}

    POST /post {userid,content}
    - Create a new post
    ** 'content':{'type':'string','required':True, 'minlength': '3', 'maxlength': '300'},
    ** 'userid':{'type':'integer','required':True}

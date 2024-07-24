API DOCUMENTATION <br>
Lambda code for a backend personal project for a "Twitter Clone" <br>
Work in Progress :)
=================

/user:

    GET /user?user=username -> {user_id, username, email, follower_ct, following_ct <- follows/email not implemented}
    - Get a users information
    ** 'user':{'type':'string','required':True}
    
    POST /user {username,password} -> (user_id)
    - Create a new user
    ** 'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
    ** 'password':{'type':'string','minlength':5,'maxlength':18,'required':True}

    /auth:

        POST /auth {username,password} -> {user_id if valid}
        - See if password is correct for a user
        ** 'username':{'type':'string','required':True}, 
           'guess' :{'type':'string','required':True}**
    
    PATCH /user/email {email}
    -not implemented 

    DELETE /user {user_id}
    -not implemented

    want to implement: 
    get following list , get followers list. These could input a user_id to join on follows

/post:

    GET /post?id=postid -> {poster_name, poster_id, content}
    - Get a post's details and comments
    ** 'post_id':{'type':'int string','required':True}

    POST /post {user_id,content} -> {post_id if valid}
    - Create a new post
    ** 'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300},
    ** 'userid':{'type':'string','required':True}

    /comments

        GET /post/comment?id=postid&start=start&limit=limit
        - Get comments from a post
        ** 'post_id':{'type':'str_int','required':True}
        ** 'start':{'type':'str_int','required':True}
        ** 'limit':{'type':'str_int','required':True}

        POST /post/comment {user_id,post_id,content}
        - Comment on a post
        ** 'post_id':{'type':'integer','required':True}
        ** 'post_id':{'type':'integer','required':True}
        ** 'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300}




/relationships

    /follow
        POST relationships/follow {follower_id, followee_id}
        - Follow a user
        ** 'follower_id':{'type':'integer'},
        ** 'followee_id':{'type':'integer'}

    /unfollow
        ** 'unfollower_id':{'type':'integer'},
        ** 'unfollowee_id':{'type':'integer'}

/like

    like a post
    not implemented

/comment

    comment on a post
    not implemented

/feed

    GET /feed/new?user=user_id&limit=limit -> [posts]
    - Gets new posts by accounts they follow
    - not implemented

    GET /feed/top?within=time&limit=limit -> [posts]
    - Gets new posts by top within a time
    - not implemented
    


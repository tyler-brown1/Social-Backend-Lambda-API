API DOCUMENTATION <br>
Lambda code for a backend personal project for a "Twitter Clone" <br>
Work in Progress :)
=================

/users:

    GET /users/username/{username} -> {user_id, username, email, follower_ct, following_ct}
    - Get a users information
    - Need to implement followers,following
    ** 'user':{'type':'string','required':True}
    
    /create

        POST /users/create {username,password} -> {user_id}
        - Create a new user
        ** 'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
        ** 'password':{'type':'string','minlength':5,'maxlength':18,'required':True}

    /auth:

        POST /auth {username,password} -> {user_id if valid}
        - See if password is correct for a user
        ** 'username':{'type':'string','required':True}, 
        ** 'guess' :{'type':'string','required':True}
    
    PATCH /users/update/{user_id} {email or username}
    -not implemented 

    DELETE /users/delete/{user_id}
    -not implemented

    GET /users/{user_id}/posts?limit&offset -> {posts:[{user_id, post_id,username, content, hours_ago}]}
    'user_id':{'type':'string','required':True, 'str_int': True},
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},

/posts:

    /create 

        POST /posts/create {user_id,content} -> {post_id if valid}
        - Create a new post
        ** 'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300},
        ** 'userid':{'type':'string','required':True}

    /{post_id}
        
        GET /posts/{post_id}?user -> {poster_name, poster_id, content, hours_ago, liked <- not implemented}
        - Get a post's details and comments
        ** 'post_id':{'type':'int string','required':True}

        /comments

            GET /posts/{post_id}/comments?offset&limit -> {comments:[{user_id, post_id,username, content, hours_ago}]}
            - Get comments from a post
            ** 'post_id':{'type':'str_int','required':True}
            ** 'offset':{'type':'str_int','required':True}
            ** 'limit':{'type':'str_int','required':True}

    /comment

        POST /posts/comment {user_id,post_id,content}
        - Comment on a post
        ** 'post_id':{'type':'integer','required':True}
        ** 'post_id':{'type':'integer','required':True}
        ** 'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300}
    
    /like

        - Not implemented

/relationships

    /follow
        POST relationships/follow {follower_id, followee_id}
        - Follow a user
        ** 'follower_id':{'type':'integer'},
        ** 'followee_id':{'type':'integer'}

    /unfollow
        ** 'unfollower_id':{'type':'integer'},
        ** 'unfollowee_id':{'type':'integer'}

/feed

    GET /feed/new?limit&offset&user -> {posts:[{user_id, post_id,username, content, hours_ago, liked}]}
    - Gets new posts by accounts they follow
    - Shows if the user liked if parameter
    - not implemented

    GET /feed/top?within&limit&user -> {posts:[{user_id, post_id,username, content, hours_ago}]}
    - Gets new posts by top within a time
    - not implemented
    


API DOCUMENTATION <br>
Lambda code for a backend personal project for a "Twitter Clone" <br>
Work in Progress :)
=================

/users:
    
    /username    || Add user qsp to see if followed

        GET /users/username/{username}?user -> {user_id, username, email, follower_ct, following_ct, following_me,am_following}
        - Get a users information
        - Need to implement followers,following
        ** 'username':{'type':'string','required':True,'str_int':True}
    
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

    /{user_id}

        GET /users/{user_id}/posts?limit&offset -> {posts:[{user_id, post_id,username, content, hours_ago}]}
        ** 'user_id':{'type':'string','required':True, 'str_int': True},
        ** 'limit':{'type':'string','required':True,'str_int':True},
        ** 'offset':{'type':'string','required':True,'str_int':True},

        /follows

            GET /users/{user_id}/follows -> {"followers":[{user_id,username}]}
            ** 'user_id':{'type':'string', 'str_int': True, 'required':True},
            ** 'limit':{'type':'string','required':True,'str_int':True},
            ** 'offset':{'type':'string','required':True,'str_int':True},

            GET /users/{user_id}/follows -> {"followers":[{user_id,username}]}
            ** 'user_id':{'type':'string','required':True, 'str_int': True},
            ** 'limit':{'type':'string','required':True,'str_int':True},
            ** 'offset':{'type':'string','required':True,'str_int':True},

        PATCH /users/{user_id}/update {email or username}
        -not implemented 

        DELETE /users/{user_id}/delete
        -not implemented

/posts:

    /create 

        POST /posts/create {user_id,content} -> {post_id if valid}
        - Create a new post
        ** 'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300},
        ** 'user_id':{'type':'integer','required':True, 'pos': True}

    /{post_id}
        
        GET /posts/{post_id}?user -> {poster_name, poster_id, content, hours_ago, liked <- not implemented}
        - Get a post's details and comments
        ** 'post_id':{'type':'string','str_int':True,'required':True},
        ** 'user_id':{'type':'string','str_int':True}

        /comment

            GET /posts/{post_id}/comment?offset&limit -> {comments:[{user_id, post_id,username, content, hours_ago}]}
            - Get comments from a post
            ** 'post_id':{'type':'string','required':True,'str_int':True},
            ** 'limit':{'type':'string','required':True,'str_int':True},
            ** 'offset':{'type':'string','required':True,'str_int':True},

            POST /posts/comment {user_id,post_id,content}
            - Comment on a post
            ** 'post_id':{'type':'integer','required':True, 'pos': True},
            ** 'user_id':{'type':'integer','required':True,'pos': True},
            ** 'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300}
        
        /like

            POST /posts/{post_id}/like
            - Like a post
            - Not implemented

            POST /posts/{post_id}/unlike
            - Remove a like
            - Not implemented

/relationships

    /follow
        POST relationships/follow {follower_id, followee_id}
        - Follow a user
        ** 'follower_id':{'type':'integer','required':True, 'pos': True},
        ** 'followee_id':{'type':'integer','required':True, 'pos': True}

    /unfollow
        ** 'unfollower_id':{'type':'integer','required':True, 'pos': True},
        ** 'unfollowee_id':{'type':'integer','required':True, 'pos': True}

/feed

    /new

        GET /feed/new?limit&offset&user -> {posts:[{user_id, post_id,username, content, hours_ago, liked}]}
        - Gets new posts, show if user liked
        ** 'user':{'type':'string', 'str_int': True}, # not required
        ** 'limit':{'type':'string','required':True,'str_int':True},
        ** 'offset':{'type':'string','required':True,'str_int':True},

    /followed

        GET /feed/followed/{user_id}?limit&offset -> {posts:[{user_id, post_id,username, content, hours_ago, liked}]}
        - Gets new posts by accounts they follow, show if user liked
        ** 'user':{'type':'string', 'str_int': True, 'required':True},
        ** 'limit':{'type':'string','required':True,'str_int':True},
        ** 'offset':{'type':'string','required':True,'str_int':True},

    /top

        GET /feed/top?within&limit&user -> {posts:[{user_id, post_id,username, content, hours_ago}]}
        - Gets new posts by top within a time
        - not implemented
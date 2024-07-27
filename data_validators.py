from cerberus import Validator
"""
Data validators for endpoints
"""

class MyValidator(Validator):

    def _validate_str_int(self, argument, field, value):
        """{'type': 'boolean'}"""
        if not (value.isdigit() and int(value)>=0):
            self._error(field,'str must be a valid int')
    
    def _validate_nonneg(self, argument, field, value):
        """{'type': 'boolean'}"""
        if value<0:
            self._error(field,'int must be nonnegative')

    def _validate_pos(self, argument, field, value):
        """{'type': 'boolean'}"""
        if value<=0:
            self._error(field,'int must be positive')
    
            
create_user = MyValidator({
    'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
    'password':{'type':'string','minlength':5,'maxlength':18,'required':True}
})
get_user = MyValidator({
    'username':{'type':'string','required':True,'str_int':True}
})
validate_user = MyValidator({
    'username':{'type':'string','required':True},
    'guess' :{'type':'string','required':True}
})
create_post = MyValidator({
    'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300},
    'user_id':{'type':'integer','required':True, 'pos': True}
})
get_post = MyValidator({
    'post_id':{'type':'string','str_int':True,'required':True},
    'user_id':{'type':'string','str_int':True}
})
follow = MyValidator({
    'follower_id':{'type':'integer','required':True, 'pos': True},
    'followee_id':{'type':'integer','required':True, 'pos': True}
})
unfollow = MyValidator({
    'unfollower_id':{'type':'integer','required':True, 'pos': True},
    'unfollowee_id':{'type':'integer','required':True, 'pos': True}
})
get_comments = MyValidator({
    'post_id':{'type':'string','required':True,'str_int':True},
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},
})
post_comment = MyValidator({
    'post_id':{'type':'integer','required':True, 'pos': True},
    'user_id':{'type':'integer','required':True,'pos': True},
    'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300}
})
get_user_posts = MyValidator({
    'user_id':{'type':'string','required':True, 'str_int': True},
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},
})
get_feed = MyValidator({ # For ones we don't need user
    'user':{'type':'string', 'str_int': True}, # not required
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},
})
get_user_follows = MyValidator({ # same for followers and following
    'user_id':{'type':'string', 'str_int': True, 'required':True},
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},
})
get_feed_followed = MyValidator({ 
    'user':{'type':'string', 'str_int': True, 'required':True},
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},
})

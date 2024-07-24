from cerberus import Validator
"""
Data validators for endpoints
"""

class MyValidator(Validator):
    def _validate_str_int(self, argument, field, value):
        """{'type': 'boolean'}"""
        return value.isdigit() and int(value)>=0
    
    def _validate_nonneg(self, argument, field, value):
        """{'type': 'boolean'}"""
        return  value>0
    
            
create_user = MyValidator({
    'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
    'password':{'type':'string','minlength':5,'maxlength':18,'required':True}
})
get_user = MyValidator({
    'user':{'type':'string','required':True}
})
validate_user = MyValidator({
    'username':{'type':'string','required':True},
    'guess' :{'type':'string','required':True}
})
create_post = MyValidator({
    'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300},
    'user_id':{'type':'integer','required':True, 'nonneg': True}
})
get_post = MyValidator({
    'post_id':{'type':'string','str_int':True,'required':True, 'nonneg': True}
})
follow = MyValidator({
    'follower_id':{'type':'integer','required':True, 'nonneg': True},
    'followee_id':{'type':'integer','required':True, 'nonneg': True}
})
unfollow = MyValidator({
    'unfollower_id':{'type':'integer','required':True, 'nonneg': True},
    'unfollowee_id':{'type':'integer','required':True, 'nonneg': True}
})
get_comments = MyValidator({
    'post_id':{'type':'string','required':True,'str_int':True},
    'limit':{'type':'string','required':True,'str_int':True},
    'offset':{'type':'string','required':True,'str_int':True},
})
post_comment = MyValidator({
    'post_id':{'type':'integer','required':True, 'nonneg': True},
    'user_id':{'type':'integer','required':True,'nonneg': True},
    'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300}
})

from cerberus import Validator
"""
Data validators for endpoints
"""

create_user = Validator({
    'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
    'password':{'type':'string','minlength':5,'maxlength':18,'required':True}
})
get_user = Validator({
    'user':{'type':'string','required':True}
})
validate_user = Validator({
    'username':{'type':'string','required':True},
    'guess' :{'type':'string','required':True}
})
create_post = Validator({
    'content':{'type':'string','required':True, 'minlength': 3, 'maxlength': 300},
    'user_id':{'type':'integer','required':True}
})
get_post = Validator({
    'post_id':{'type':'integer','required':True}
})


from cerberus import Validator
create_user = Validator({
    'username':{'type':'string','minlength':4,'maxlength':12,'required':True},
    'password':{'type':'string','minlength':5,'maxlength':18,'required':True}
})
get_user = Validator({
    'username':{'type':'string','required':True}
})


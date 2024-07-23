from cerberus import Validator
create_user = Validator({
    'username':{'type':'string','minlength':4,'maxlength':12},
    'password':{'type':'string','minlength':5,'maxlength':18}
})

from app.utils import get_time

class User:
    def __init__(self, id : str, name, password, role_):
        user_id = id
        username = name
        user_password = password
        role = role_
        join_time = get_time()
        submit_count = "0" 
        resolve_time = "0"
        is_banned = False
        
        
from user import User

class UserList:
    def __init__(self):
        self.users_dict = {}
        
    def add_user(self, name, user_id, message=None, date=None, region_id=None, region_type=None, membership=None):
        existing_user = next((user for user in self.users_list if user.id == user_id), None)
        if existing_user:
            existing_user.add_message(message)
            existing_user.add_region(region_id, region_type)
            existing_user.add_messages_count()
            existing_user.add_dates(date)
            existing_user.membership = membership
        else:
            new_user = User(user_id, name, message, date)
            if region_id is not None and region_type is not None:
                new_user.add_region(region_id, region_type)
            new_user.membership = membership
            self.users_list.append(new_user)

    def get_user(self, user_id):
        for user in self.users_list:
            if user_id in user.id:
                return user
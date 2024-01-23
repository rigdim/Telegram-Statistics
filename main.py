from chat_data.user_list import UserList

user_list = UserList()

user_list.add_user(name="John Doe", user_id="123", message="Hello!", date="2022-01-01", region_id="1", region_type="city", membership="Yes")

for user in user_list:
    user.display_info()
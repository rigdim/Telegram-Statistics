import json
import re
from datetime import datetime
from fuzzywuzzy import fuzz

class User:
    def __init__(self, name, user_id, message):
        self.name = name
        self.user_id = user_id
        self.message = message
        self.message_count = 1  # Initialize message count to 1
        self.regions_count = {}  # Dictionary to store region counts
        self.region_type = ''

    def add_region(self, region_id):
        # Add or update the count for the specified region
        self.regions_count[region_id] = self.regions_count.get(region_id, 0) + 1

    def add_message_count(self):
        self.message_count += 1

    def display_user_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.user_id}")
        print(f"Message: {self.message}")
        print(f"Message Count: {self.message_count}")

        # Sort dictionary descending.
        sorted_regions=sort_dict(self.regions_count)
        # Display the first (max) element from the sorted dictionary.
        (first_region, count) = get_first_region(sorted_regions)
        print(sorted_regions)
        if first_region is None:
            print("Region not found!")
        else:
            print(f"Region: {regions[first_region]['match'][0]} {count}")
        print("---")
        input()


def sort_dict(dictionary):
     return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))


def get_first_region(dictionary):
    if dictionary:
        for key, value in dictionary.items():
            if key is not None:
                return key, value


def add_user(users_list, name, user_id, message, region_id=None):
    # Check if the user with the given user_id already exists.
    existing_user = next((user for user in users_list if user.user_id == user_id), None)
    if existing_user:
        # User already exists, update the existing user.
        existing_user.add_region(region_id)  # You can add a check for None if needed.
        existing_user.add_message_count()
    else:
        # User does not exist, create a new user and add to the list.
        new_user = User(name, user_id, message)
        if region_id is not None:
            new_user.add_region(region_id)
        users_list.append(new_user)


users_list = []

# TODO: add display name for city and for district.
regions = [
    { 'match': [ 'Иркутск' ] },
    { 'match': [ 'Ангарск' ] },
    { 'match': [ 'Братск' ] },
    { 'match': [ 'Усть-Илимск' ] },
    { 'match': [ 'Усоль' ] },
    { 'match': [ 'Тайшет' ] },
    { 'match': [ 'Шелехов' ] },
    { 'match': [ 'г. Черемхово' ] },
    { 'match': [ 'Нижнеудинск' ] },
    { 'match': [ 'Усть-Кут' ] },
    { 'match': [ 'Нижнеилимск' ] },
    { 'match': [ 'Зим' ] },
    { 'match': [ 'Слюдян' ] },
    { 'match': [ 'Тулун' ] },
    { 'match': [ 'Саянск', ] },
    { 'match': [ 'Эхирит-Булагатск' ] },
    { 'match': [ 'Черемхов' ] },
    { 'match': [ 'Куйтун' ] },
    { 'match': [ 'Чунск' ] },
    { 'match': [ 'Залари' ] },
    { 'match': [ 'Бохан' ] },
    { 'match': [ 'Аларск', 'Кутулик' ] },
    { 'match': [ 'Осинск' ] },
    { 'match': [ 'Киренск' ] },
    { 'match': [ 'Свирск' ] },
    { 'match': [ 'Качуг' ] },
    { 'match': [ 'Казачинско-Ленск' ] },
    { 'match': [ 'Нукутск' ] },
    { 'match': [ 'Усть-Уд' ] },
    { 'match': [ 'Бодайб' ] },
    { 'match': [ 'Усть-Илимск' ] },
    { 'match': [ 'Баяндаевск', 'Баяндай' ] },
    { 'match': [ 'Ольхон' ] },
    { 'match': [ 'Жигалов' ] },
    { 'match': [ 'Балаганск' ] },
    { 'match': [ 'Мамско-Чуйск', 'Мама' ] },
    { 'match': [ 'Катангск' ] }
]

# Word endings for region comparemet.
region_endings = [ 'ий', 'ого', 'ому', 'им', 'ом' ] 

# Check if the last letters are equal to the provided ending.
def check_ending(str, ending):

    last_letters = str[-len(ending):]

    return last_letters == ending


def find_region_mention(text):

    words = re.split('\\. |\\, |\\.| ', text)

    # Check each word for similarity to region names.
    for word in words:
        for index, region in enumerate(regions):
            for region_match in region['match']:
                if region_match in word:
                    for ending in region_endings:
                        if check_ending(word, ending):
                            return index
                        return index
    

def parse_telegram_to_excel():
    with open('./docs/result.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for message in data["messages"]:

        if message["type"] != "message":
            continue

        id = message["id"]
        user_name = message["from"]
        user_id = message["from_id"]
        date = datetime.strptime(message["date"].replace("T", " "), "%Y-%m-%d %H:%M:%S")
        text = message["text"]

        if type(text) == list:
            txt_content = ""
            for part in text:
                if type(part) == str:
                    txt_content += part
            text = txt_content

        text = text.replace("\n", " ")
        # Create user or get already existed.
        region_id = find_region_mention(text)
        add_user(users_list, user_name, user_id, text, region_id)
        
    for user in users_list:
        user.display_user_info()

# Call the function to execute the code.
parse_telegram_to_excel()
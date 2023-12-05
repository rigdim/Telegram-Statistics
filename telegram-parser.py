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

    def display_user_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.user_id}")
        print(f"Message: {self.message}")
        print(f"Message Count: {self.message_count}")

        # Sort dictionary descending.
        sorted_regions=sort_dict(self.regions_count)
        # Display the first (max) element from the sorted dictionary.
        (first_region, count) = get_first_dict(sorted_regions)
        if first_region:
            print(f"Region: {regions[first_region]['match'][0]} {count}")
        else:
            print("Регион не найден")
        print("---")

def sort_dict(dictionary, reverse=False):
     return dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=reverse))


def get_first_dict(dictionary):
    if dictionary:
        first, value = next(iter(dictionary.items()))
        return first, value
    else:
        return -1, None


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
        # Create user.
        user = User(name=user_name, user_id=user_id, message=text)
        index = find_region_mention(text)
        user.add_region(index)
        user.display_user_info()

# Call the function to execute the code.
parse_telegram_to_excel()
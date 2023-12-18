import json
import pandas as pd
import re
from pymystem3 import Mystem
from datetime import datetime


class User:
    def __init__(self, name, user_id, message):
        self.name = name
        self.user_id = user_id
        self.messages = message
        self.messages_count = 1
        self.regions_count = {}  # Nested dictionary to store the region ID and the number of mentions of both as a city and as a district.
        self.region = None

    def add_message(self, message):
        self.messages += '\n' + message

    def add_region(self, region_id, region_type):
        # Add or update the count for the specified region and type.
        region_dict = self.regions_count.get(region_id, {"city": 0, "district": 0})
        if region_type is not None:
            region_dict[region_type] += 1
        self.regions_count[region_id] = region_dict

    def add_messages_count(self):
        self.messages_count += 1

    def display_user_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.user_id}")
        print(f"Message: {self.messages[:200]}")
        print(f"Message Count: {self.messages_count}")

        # Sort dictionary descending.
        sorted_regions = sort_dict(self.regions_count)
        for key, value in sorted_regions.items():
            if key is not None:
                print(f"* {regions[key]['match'][0]} - city: {value.get('city')}, district: {value.get('district')}")

        if self.region is None:
            print("Region not found!")
        else:
            print(f"Region: {self.region}")
        print("-----")

    # Get an appropriate region display name based on 'city' and 'district' number of mentions.
    def set_region(self):
        first_region, mentions = get_first_region(sort_dict(self.regions_count))

        if first_region is not None:
            city_count = mentions.get("city", 0)
            district_count = mentions.get("district", 0)
            if (city_count > district_count) and ('name_city' in regions[first_region]):
                self.region = regions[first_region]['name_city']
            elif ('name_district' in regions[first_region]):
                self.region = regions[first_region]['name_district']
            else:
                self.region = None
        
        
# Sort regions by sum of its mentions as a city and as a district.
def sort_dict(dictionary):
     return dict(sorted(dictionary.items(), key=lambda item: sum(item[1].values()), reverse=True))


def get_first_region(dictionary):
    if dictionary is not None:
        for key, value in dictionary.items():
            if key is not None:
                return key, value
    return None, None   
            

def add_user(users_list, name, user_id, message, region_id=None, region_type=None):
    # Check if the user with the given user_id already exists.
    existing_user = next((user for user in users_list if user.user_id == user_id), None)
    if existing_user:
        # User already exists, update the existing user.
        existing_user.add_message(message)
        existing_user.add_region(region_id, region_type)
        existing_user.add_messages_count()
    else:
        # User does not exist, create a new user and add to the list.
        new_user = User(name, user_id, message)
        if region_id is not None and region_type is not None:
            new_user.add_region(region_id, region_type)
        users_list.append(new_user)


users_list = []


def users_to_excel():
    data = {
        "ID": [user.user_id for user in users_list],
        "Имя": [user.name for user in users_list],
        "Сообщений": [user.messages_count for user in users_list],
    }

    # Add a column for the most frequently occurring region for each user.
    data["Регион"] = [
        user.region for user in users_list
    ]

    df = pd.DataFrame(data)

    df = df.sort_values(by="Сообщений", ascending=False)

    # unique_regions = df["Регион"].unique()
    # region_colors = {region: f"#{np.random.randint(0x999999, 0xFFFFFF):06x}" for region in unique_regions}

    styled_df = (
        df.style
        .set_table_styles([{"selector": "", "props": [("border", "1px solid black")]}])  # Add default black borders.
        .bar(subset=["Сообщений"], color='lightblue', vmin=0)  # Color cells in the "Количество сообщений" column.
        .highlight_max(subset=["Сообщений"], color='yellow')  # Highlight maximum value in the "Количество сообщений" column.
        # .apply(lambda row: [f"background-color: {region_colors[row['Регион']]}"] * len(row), axis=1, subset=["Регион"])
    )

    with pd.ExcelWriter('./docs/Соотнесение пользователей с регионом.xlsx', engine='openpyxl') as writer:
    
        # Write the DataFrame to the Excel file.
        styled_df.to_excel(writer, sheet_name='Пользователи и регионы', index=False)

        workbook  = writer.book
        worksheet = writer.sheets['Пользователи и регионы']

        worksheet.column_dimensions['A'].width = 16
        worksheet.column_dimensions['B'].width = 30
        worksheet.column_dimensions['C'].width = 12
        worksheet.column_dimensions['D'].width = 30


regions = [
    { 'match': [ 'Иркутск' ], 'name_city': 'Иркутск', 'name_district': 'Иркутский район' },
    { 'match': [ 'Ангарск' ], 'name_district': 'Ангарский ГО' },
    { 'match': [ 'Братск' ], 'name_city': 'Братск', 'name_district': 'Братский район' },
    { 'match': [ 'Усть-Илимск' ], 'name_city': 'Усть-Илимск', 'name_district': 'Усть-Илимский район' },
    { 'match': [ 'Усоль' ], 'name_city': 'Усолье-Сибирское', 'name_district': 'Усольский район' },
    { 'match': [ 'Тайшет' ], 'name_city': 'Тайшет', 'name_district': 'Тайшетский район' },
    { 'match': [ 'Шелехов' ], 'name_district': 'Шелеховский  район' },
    { 'match': [ 'Черемхов' ], 'name_city': 'Черемхово', 'name_district': 'Черемховский район' },
    { 'match': [ 'Нижнеудинск' ], 'name_district': 'Нижнеудинский район' },
    { 'match': [ 'Усть-Кут' ], 'name_district': 'Усть-Кутский район' },
    { 'match': [ 'Нижнеилимск' ], 'name_district': 'Нижнеилимский район' },
    { 'match': [ 'Зим' ], 'name_district': 'г. Зима и Зиминский район' },
    { 'match': [ 'Слюдян' ], 'name_district': 'Слюдянский район' },
    { 'match': [ 'Тулун' ], 'name_city': 'Тулун', 'name_district': 'Тулунский район' },
    { 'match': [ 'Саянск', ], 'name_city': 'Саянск' },
    { 'match': [ 'Эхирит-Булагатск', 'Усть-Ордынск' ], 'name_district': 'Эхирит-Булагатский район' },
    { 'match': [ 'Куйтун' ], 'name_district': 'Куйтунский район' },
    { 'match': [ 'Чунск' ], 'name_district': 'Чунский район' },
    { 'match': [ 'Залари' ], 'name_district': 'Заларийский район' },
    { 'match': [ 'Бохан' ], 'name_district': 'Боханский район' },
    { 'match': [ 'Аларск', 'Кутулик' ], 'name_district': 'Аларский район' },
    { 'match': [ 'Осинск' ], 'name_district': 'Осинский район' },
    { 'match': [ 'Киренск' ], 'name_district': 'Киренский район' },
    { 'match': [ 'Свирск' ], 'name_district': 'Свирский район' },
    { 'match': [ 'Качуг' ], 'name_district': 'Качугский район' },
    { 'match': [ 'Казачинско-Ленск' ], 'name_district': 'Казачинско-Ленский район' },
    { 'match': [ 'Нукутск' ], 'name_district': 'Нукутский район' },
    { 'match': [ 'Усть-Уд' ], 'name_district': 'Усть-Удинский район' },
    { 'match': [ 'Бодайб' ], 'name_district': 'Бодайбинский район' },
    { 'match': [ 'Баяндаевск', 'Баяндай' ], 'name_district': 'Баяндаевский район' },
    { 'match': [ 'Ольхон' ], 'name_district': 'Ольхонский район' },
    { 'match': [ 'Жигалов' ], 'name_district': 'Жигаловский район' },
    { 'match': [ 'Балаганск' ], 'name_district': 'Балаганский район' },
    { 'match': [ 'Мамско-Чуйск', 'Мама' ], 'name_district': 'Мамско-Чуйский район' },
    { 'match': [ 'Катангск' ], 'name_district': 'Катангский район' }
]


# Word endings to be recognized as district.
region_endings = [ 'ий', 'ого', 'ому', 'им', 'ом' ] 


# Check if the last letters are equal to the provided ending.
def check_ending(str, ending):
    last_letters = str[-len(ending):]
    return last_letters == ending


def find_region_mention(text):

    words = re.split(r'\. |, |\.| ', text)

    for word in words:
        for index, region in enumerate(regions):
            for region_match in region['match']:
                if region_match in word:
                    for ending in region_endings:
                        if check_ending(word, ending):
                            return index, "district"
                    return index, "city"
    return None, None


# Load .json file and get users data from it.
def get_users_data():
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

        # Create user with region that was founded or update already existed.
        region_id, region_type = find_region_mention(text)
        add_user(users_list, user_name, user_id, text, region_id, region_type)
        
    for user in users_list:
        user.set_region()
        user.display_user_info()


# Keywords with their variations
keywords = [
    {"электроэнергии", "электричество", "свет"},
    {"сеть", "сс"},
    {"авария", "происшествие", "поломка"}
]

# Dictionary to store the pivot table data
pivot_table_data = {}

mystem = Mystem()

# Normalize keywords using pymystem3
def normalize_word(word):
    lemmas = mystem.lemmatize(word.lower())
    return lemmas[0].strip() if lemmas else word.lower()

def create_pivot_table():
    
    print("Start")
    # Initialize pivot table data
    for region in regions:
        region_name_city = region.get("name_city", 0)
        region_name_district = region.get("name_district", 0)
        if region_name_city:
            pivot_table_data[region_name_city] = {keyword: 0 for keyword_set in keywords for keyword in keyword_set}
        if region_name_district:
            pivot_table_data[region_name_district] = {keyword: 0 for keyword_set in keywords for keyword in keyword_set}

    # Update pivot table data based on user messages
    for user in users_list:
        for keyword_set in keywords:
            for keyword in keyword_set:
                if user.region and keyword in user.messages:
                    pivot_table_data[user.region][keyword] += 1

    # Create a DataFrame from pivot_table_data
    pivot_table_df = pd.DataFrame.from_dict(pivot_table_data, orient="index")

    # Write the pivot table DataFrame to the Excel file
    with pd.ExcelWriter('./docs/Соотнесение пользователей с регионом.xlsx', engine='openpyxl', mode='a') as writer:
        pivot_table_df.to_excel(writer, sheet_name='Статистика по проблемам', index=True)
    print("End")


# Call the function to execute the code.
get_users_data()
users_to_excel()
create_pivot_table()
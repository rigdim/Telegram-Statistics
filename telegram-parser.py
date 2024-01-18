import json
import pandas as pd
import re
import sys
import calendar
import numpy as np
from pymystem3 import Mystem
from datetime import datetime, timedelta
from openpyxl.styles import Border, Side
import xlsxwriter.utility as Utility

class User:
    def __init__(self, id, name, message, date):
        self.id = id
        if name is None:
            self.name = 'Удаленный пользователь'
        else:
            self.name = name
        self.messages = message
        if message:
            self.messages_count = 1
            self.messages_dates = [(date, 1)]
        else:
            self.messages_count = 0
            self.messages_dates = []
        self.regions_count = {}  # Nested dictionary to store the region ID and the number of mentions of both as a city and as a district.
        self.region = None
        self.membership = None

    def add_message(self, message):
        self.messages += '\n' + message

    # Counts messages by date.
    def add_dates(self, date):
        result = next((messages_date for messages_date in self.messages_dates if messages_date[0] == date), None)
        if result is None:
            self.messages_dates.append((date, 1))
        else:
            date_index = self.messages_dates.index(result)
            self.messages_dates[date_index] = (result[0], result[1] + 1)

    def add_region(self, region_id, region_type):
        # Add or update the count for the specified region and type.
        region_dict = self.regions_count.get(region_id, {"city": 0, "district": 0})
        if region_type is not None:
            region_dict[region_type] += 1
        self.regions_count[region_id] = region_dict

    def add_messages_count(self):
        self.messages_count += 1

    def display_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.id}")
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

        print(f"Dates: {self.messages_dates}")
        print(f"Membership: {self.membership}")
        print("-" * 10)


    def get_first_region(self, ):
        if self.regions_count is not None:
            sorted_regions = sort_dict(self.regions_count)
            for key, value in sorted_regions.items():
                if key is not None:
                    return key, value
        return None, None
    
    # Get an appropriate region display name based on 'city' and 'district' number of mentions.
    def set_region(self):
        if self.regions_count is not None:
            first_region, mentions = self.get_first_region()
            if first_region is not None:
                city_count = mentions.get("city", 0)
                district_count = mentions.get("district", 0)
                if (city_count > district_count) and ('name_city' in regions[first_region]):
                    self.region = regions[first_region]['name_city']
                elif ('name_district' in regions[first_region]):
                    self.region = regions[first_region]['name_district']
                else:
                    self.region = None 

    def get_last_dates_count(self, last_days):
        if self.messages_dates is not None:
            messages_count = 0
            for date, count in reversed(self.messages_dates):
                if date < (datetime.now() - timedelta(days = last_days)).date():
                    break
                messages_count += count
            return messages_count
        
    def get_date_distribution(self, start_year, end_year):
        if self.messages_dates is not None:
            
            # Create array with years * 12 cells.
            date_distribution = []
            date_distribution.extend([0] * ((end_year - start_year + 1) * 12))

            # Counts messages by each month and year and put it in array.
            for date, count in self.messages_dates:
                if date.year >= start_year:
                    date_distribution[(date.year - start_year) * 12 + date.month - 1] += count
            return date_distribution
            
def add_user(users_list, name, id, message = None, date = None, region_id = None, region_type = None, membership = None):
    # Check if the user with the given user_id already exists.
    existing_user = next((user for user in users_list if user.id == id), None)
    if existing_user:
        # User already exists, update the existing user.
        existing_user.add_message(message)
        existing_user.add_region(region_id, region_type)
        existing_user.add_messages_count()
        existing_user.add_dates(date)
        existing_user.membership = membership
    else:
        # User does not exist, create a new user and add to the list.
        new_user = User(id, name, message, date)
        if region_id is not None and region_type is not None:
            new_user.add_region(region_id, region_type)
        new_user.membership = membership
        users_list.append(new_user)

def get_user(id):
    for user in users_list:
        if id in user.id:
            return user
                
users_list = []


# Sort regions by sum of its mentions as a city and as a district.
def sort_dict(dictionary):
     if dictionary is not None:
        return dict(sorted(dictionary.items(), key=lambda item: sum(item[1].values()), reverse=True))


# Define class for region as a group header for several users.
class Region():
    def __init__(self, name, region_type):
        self.id = len(regions_list) + 1
        self.name = name
        self.region_type = region_type
        self.membership = "Нет"
        self.users = []
        self.users_count = 0
        regions_list.append(self)
    
    def add_user(self, user):
        self.users.append(user)
        self.users_count += 1

    def get_messages_count(self):
        messages_count = 0
        for user in self.users:
            messages_count += user.messages_count
        return messages_count
    
    def get_last_dates_count(self, days):
        messages_count = 0
        for user in self.users:
            messages_count += user.get_last_dates_count(days)
        return messages_count

    def get_date_distribution(self, start_year, end_year):
        # Create array with years * 12 cells.
        date_distribution = []
        date_distribution.extend([0] * ((end_year - start_year + 1) * 12))

        if self.users:
            # Sum messages of user for each month and year.
            sum_month = 0
            for month in range((end_year - start_year + 1) * 12):
                for user in self.users:
                    sum_month += user.get_date_distibution
                date_distribution[month] = sum_month
        return date_distribution

    def display_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.id}")
        print(f"Message Count: {self.get_messages_count()}")
        print(f"Users count: {self.users_count}")
        print(f"Type: {self.region_type}")
        print("-" * 10)
        
# All displayable regions.
regions_list = []

def fill_regions_list():
    for region in regions:
        name = region.get("name_city", 0)
        if name:
            region_type = "Город"
            Region(name, region_type)

        name = region.get("name_district", 0)
        if name:
            region_type = "Район (ГО)"
            Region(name, region_type)

regions = [
    { 'match': [ 'Иркутск' ], 'name_city': 'Иркутск', 'name_district': 'Иркутский район' },
    { 'match': [ 'Ангарск' ], 'name_district': 'Ангарский ГО' },
    { 'match': [ 'Братск' ], 'name_city': 'Братск', 'name_district': 'Братский район' },
    { 'match': [ 'Усть-Илимск' ], 'name_city': 'Усть-Илимск', 'name_district': 'Усть-Илимский район' },
    { 'match': [ 'Усоль' ], 'name_city': 'Усолье-Сибирское', 'name_district': 'Усольский район' },
    { 'match': [ 'Тайшет' ], 'name_district': 'Тайшетский район' },
    { 'match': [ 'Шелехов' ], 'name_district': 'Шелеховский  район' },
    { 'match': [ 'Черемхов' ], 'name_city': 'Черемхово', 'name_district': 'Черемховский район' },
    { 'match': [ 'Нижнеудинск' ], 'name_district': 'Нижнеудинский район' },
    { 'match': [ 'Усть-Кут' ], 'name_district': 'Усть-Кутский район' },
    { 'match': [ 'Нижнеилимск' ], 'name_district': 'Нижнеилимский район' },
    { 'match': [ 'Зим' ], 'name_district': 'г. Зима и Зиминский район' },
    { 'match': [ 'Слюдян' ], 'name_district': 'Слюдянский район' },
    { 'match': [ 'Тулун' ], 'name_city': 'Тулун', 'name_district': 'Тулунский район' },
    { 'match': [ 'Саянск' ], 'name_city': 'Саянск' },
    { 'match': [ 'Эхирит-Булагатск', 'Усть-Ордынск' ], 'name_district': 'Эхирит-Булагатский район' },
    { 'match': [ 'Куйтун' ], 'name_district': 'Куйтунский район' },
    { 'match': [ 'Чунск' ], 'name_district': 'Чунский район' },
    { 'match': [ 'Залари' ], 'name_district': 'Заларийский район' },
    { 'match': [ 'Бохан' ], 'name_district': 'Боханский район' },
    { 'match': [ 'Аларск', 'Кутулик' ], 'name_district': 'Аларский район' },
    { 'match': [ 'Осинск' ], 'name_district': 'Осинский район' },
    { 'match': [ 'Киренск' ], 'name_district': 'Киренский район' },
    { 'match': [ 'Свирск' ], 'name_city': 'Свирск' },
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

# Get .json file data or get None.
def open_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return None
    return data


def get_users_data():
    export_file_path = './docs/result.json'
    data = open_json(export_file_path)

    # Get data from messages export.
    if data is not None:
        for message in data["messages"]:
            if message["type"] != "message":
                continue

            message_id = message["id"]
            user_id = message["from_id"]
            user_name = message["from"]
            date = datetime.strptime(message["date"].replace("T", " "), "%Y-%m-%d %H:%M:%S").date()
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
            add_user(users_list, user_name, user_id, text, date, region_id, region_type)

    members_file_path = './docs/members.json'
    members = open_json(members_file_path)

    # Check that users from messages are still members in chat.
    if members is not None:
        for member in members:
            user = get_user(member["id"])
            if user:
                user.membership = 'Да'
            else:
                add_user(users_list, member["name"], member["id"], message = None, date = None, membership="Да")

        for user in users_list:
            if user.membership is None:
                user.membership = "Нет"

    for user in users_list:
        user.set_region()
        user.display_info()

    get_regions_data()


def get_regions_data():

    fill_regions_list()

    for region in regions_list:
        for user in users_list:
            if user.region == region.name:
                region.add_user(user)

        region.display_info()

# Define rules to highlight cells.
highlight_values = [
    {'value': 'Нет', 'color': 'background-color: #DD3333'},
    {'value': 'Удаленный пользователь', 'color': 'background-color: #DD8888', 'entire_row': True},
    {'value': 'Район (ГО)', 'color': 'background-color: #EEEEEE', 'entire_row': True},
    {'value': 'Город', 'color': 'background-color: #EEEEEE', 'entire_row': True},

]

def highlight_by_value(row):
    for highlight in highlight_values:
        for col, val in row.items():
            if val == highlight['value']:
                if highlight.get('entire_row', False):
                    return [highlight['color'] for _ in row.index]
                else:
                    return [highlight['color'] if v == val else '' for v in row]
    return [''] * len(row.index)


# Define a custom sorting key function. Keys are similar to pandas DataFrame sorting.
def custom_sort(user):
     return (user.region is None, user.region, -user.messages_count)


def users_to_excel():    

    # TODO: Change start and end dates with the oldest and the newest message date.
    now = datetime.now()
    start_year = 2022
    end_year = now.year
    years = end_year - start_year + 1
    months_columns = [f'{calendar.month_abbr[month + 1]} {year % 100}' for year in range(start_year, end_year + 1) for month in range(12)]

    data_users = {
        "object": [user for user in users_list],
        "ID": [user.id for user in users_list],
        "Имя": [user.name for user in users_list],
        "Сообщений": [user.messages_count if user.messages_count is not None else 0 for user in users_list],
        "Регион": [user.region for user in users_list],
        "В группе": [user.membership for user in users_list],
        "Актив 14 дн.": [user.get_last_dates_count(14) if user.get_last_dates_count(14) is not 0 else '' for user in users_list],
        "Актив 30 дн.": [user.get_last_dates_count(30) if user.get_last_dates_count(30) is not 0 else '' for user in users_list],
        "Актив 90 дн.": [user.get_last_dates_count(90) if user.get_last_dates_count(90) is not 0 else '' for user in users_list]
    }

    df_users = pd.DataFrame(data_users)

    # Insert messages distribution in DataFrame.
    if start_year > end_year:
        print('Начальная дата распределения сообщений более поздняя, чем конечная.')
    else:
        df_users['date_distribution'] = df_users.apply(lambda row: row['object'].get_date_distribution(start_year, end_year), axis=1)

        # Create and rename index for DataFrame with date distribution.
        df_distribution = pd.DataFrame(df_users['date_distribution'].tolist(), index=df_users.index)
        df_distribution.columns = months_columns

        # Concat date distribution with other data.
        df_users = pd.concat([df_users, df_distribution], axis=1)

        # Where to place additional data on sheet.
        start_column_additional_data = df_users.shape[1] - years * 12

        # Insert columns for sparklines.
        df_users.insert(start_column_additional_data, '', value=np.nan)
        for year in reversed(range(start_year, end_year + 1)):
            df_users.insert(start_column_additional_data, str(year) + ' г.', value=np.nan)

    data_regions = {
        "object": [region for region in regions_list],
        "ID": [0 for _ in regions_list],
        "Имя": [region.name for region in regions_list],
        "Сообщений": [0 for _ in regions_list],
        "Регион": [region.name for region in regions_list],
        "В группе": [region.region_type for region in regions_list],
        "Актив 14 дн.": [region.get_last_dates_count(14) if region.get_last_dates_count(14) is not 0 else '' for region in regions_list],
        "Актив 30 дн.": [region.get_last_dates_count(30) if region.get_last_dates_count(30) is not 0 else '' for region in regions_list],
        "Актив 90 дн.": [region.get_last_dates_count(90) if region.get_last_dates_count(90) is not 0 else '' for region in regions_list]
    }
    
    df_regions = pd.DataFrame(data_regions)

    # Find sum of all messages.
    region_messages_sum = df_users.groupby("Регион")["Сообщений"].sum().reset_index()
    df_regions = pd.merge(df_regions, region_messages_sum, on="Регион", how="left", suffixes=('', '_sum'))
    df_regions['Сообщений'] = df_regions['Сообщений_sum'].fillna(df_regions['Сообщений']).astype(int)
    df_regions = df_regions.drop(['Сообщений_sum'], axis=1)
    
    if start_year <= end_year:
        # Find sum of messages by months for regions.
        df_regions_sum = df_users.groupby('Регион')[months_columns].sum().reset_index()
        df_regions = pd.merge(df_regions, df_regions_sum, how='left', on='Регион')
        df_users = df_users.drop('date_distribution', axis=1)

    # Sort regions to set indexes.
    df_regions = df_regions.sort_values(by=["Регион", "Сообщений"], ascending=[True, False])
    df_regions['ID'] = df_regions.reset_index().index + 1

    # Concat, sort DataFrames, delete temporary columns.
    df = pd.concat([df_users, df_regions], ignore_index=True)
    df = df.sort_values(by=["Регион", "Сообщений", "ID"], ascending=[True, False, True])
    df = df.drop(['object', 'Регион'], axis=1)

    styled_df = (
        df.style
        .bar(subset=["Сообщений"], color='lightblue', vmin=0)  # Color cells in the "Количество сообщений" column.
        .highlight_max(subset=["Сообщений"], color='yellow')  # Highlight maximum value in the "Количество сообщений" column.
        .apply(highlight_by_value, axis=1)
    )

    workbook_name = 'Соотнесение пользователей с регионом.xlsx'
    workbook_path = './docs/' + workbook_name
    worksheet_name = 'Пользователи и регионы'

    with pd.ExcelWriter(workbook_path, engine='xlsxwriter') as writer:

        styled_df.to_excel(writer, worksheet_name, index=False) 

        worksheet = writer.book.get_worksheet_by_name(worksheet_name)

        if start_year <= end_year:
            # Where sparklines start.
            start_column_additional_data = df.shape[1] - years * 12 - years
            
            # Add sparklines for each year.
            for period in range(years):
                for row in range(df.shape[0]):
                    target_cell = get_cell_address(row + 1, period + start_column_additional_data - 1) # Where are sparklines located.
                    rng = get_range_address(row + 1, start_column_additional_data + years + period * 12, row + 1, start_column_additional_data + years + (period + 1) * 12 - 1) # Range of cells with messages count.
                    worksheet.add_sparkline(target_cell, {'range': rng, 'type': 'column', 'max': 10}) # Adds sparkline. Defines type, width and max value.
        else:
            start_column_additional_data = df.shape[1]
            years = 1
        
        # Using conditional formation for proper borders.
        border_format = writer.book.add_format({'border': 1, 'border_color': 'black'})
        worksheet.conditional_format(get_range_address(0, 0, df.shape[0], start_column_additional_data + years - 2), {'type':'cell', 'criteria': '<>', 'value': -1, 'format': border_format})
        
        worksheet.autofit()


def get_cell_address(row, col):
    return Utility.xl_rowcol_to_cell(row, col)

def get_range_address(fitst_row, fitst_col, second_row, second_col):
    return Utility.xl_range(fitst_row, fitst_col, second_row, second_col)


# Keywords with their variations.
keywords = [
    ["электроэнергия", "электричество", "свет", "ээ", "эл", "э", "отключение"],
    ["сеть", "связь", "соединение"],
    ["авария", "происшествие", "поломка"],
    ["ПК", "АРМ"],
    ["карточки"]
]


# Dictionary to store the pivot table data.
pivot_table_data = {}

mystem = Mystem()


# Normalize keywords using pymystem3.
def normalize_words(words):
    lemmas = mystem.lemmatize(words.lower())
    lemmatized_words = [word for word in lemmas if word.isalpha()]
    if len(lemmatized_words) == 1:
        return lemmatized_words[0]
    return lemmatized_words


# Count words and delete duplicates.
def word_count(text):
    words = re.split(r'\\|/|\n|\. |, |\.| ', text)
    cleared_words = [word for word in words if word.isalpha()]
    word_dict = {}
    for clear_word in cleared_words:
        clear_word = clear_word.lower()
        word_dict[clear_word] = word_dict.get(clear_word, 0) + 1
    return word_dict


def find_word_number(target_word, text):
    try:
        word_number = text.index(target_word)
        return word_number
    except ValueError:
        return None


def find_keyword(keyword, text):

    if len(keyword) > 2:
        nomalized_keyword = normalize_words(keyword)
    else:
        nomalized_keyword = keyword

    normalized_words = normalize_words(text)

    if nomalized_keyword in normalized_words:
        return find_word_number(nomalized_keyword, normalized_words)
    else:
        return -1


def create_pivot_table():

    # Initialize pivot table.
    for i, region in enumerate(regions_list):
        
        show_progress(iteration=i, total=len(regions), suffix=region.name)

        pivot_table_data[region.name] = {", ".join(keyword_set): 0 for keyword_set in keywords}

        all_region_messages = ""
        clear_messages = ""

        # Get all messages for corresponding region.
        for user in users_list:
            if user.region == region.name:
                all_region_messages += " " + user.messages

        word_count_dict =  word_count(all_region_messages)

        for word in word_count_dict.keys():
            clear_messages += " " + word

        # Check if keyword in messages and fill out it to the table.
        for keyword_set in keywords:
            for keyword in keyword_set:
                position = find_keyword(keyword, clear_messages)
                if position >= 0:
                    pivot_table_data[region.name][", ".join(keyword_set)] += list(word_count_dict.values())[position]
            
    pivot_table_df = pd.DataFrame.from_dict(pivot_table_data, orient="index")

    with pd.ExcelWriter('./docs/Проблемы.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        pivot_table_df.to_excel(writer, sheet_name='Статистика по проблемам', index=True)

        worksheet = writer.sheets['Статистика по проблемам']

        add_borders(worksheet)
        set_autowidth(worksheet)


def add_borders(worksheet):
    for row in worksheet.rows:
        for cell in row:
            cell.border = Border(left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin'))


def get_column_letter(col):
    return Utility.xl_col_to_name(col)


def set_autowidth(worksheet):
    for index, col, in enumerate(worksheet.columns):
        max_length = 0
        min_width = 8
        column = [cell for cell in col]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 3)
        if adjusted_width < min_width:
            adjusted_width = min_width
        worksheet.column_dimensions[get_column_letter(index)].width = adjusted_width


def show_progress(iteration, total, prefix='Прогресс:', suffix='', length=25, fill='█'):
    if total <= 50:
        length = total
    if iteration == (total - 1):
        percent = 100.0
        bar = fill * length
    else:
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()


# Call the function to execute the code.
print("СООТНЕСЕНИЕ ПОЛЬЗОВАТЕЛЯ С РЕГИОНОМ")
get_users_data()
users_to_excel()
print("\nПОДСЧЕТ КОЛИЧЕСТВА ИНЦИДЕНТОВ")
create_pivot_table()
import json
import pandas as pd
import re
import sys
import calendar
import numpy as np
from enum import Enum
from pymystem3 import Mystem
from datetime import datetime, timedelta
import xlsxwriter.utility as Utility

class DictElement:
    """ Родительский класс для объектов User, Message, Region. """
    def to_dict(self):
        """ Преобразование полей объекта и их значений в словарь. Используется для сохранения в JSON. """
        return vars(self)

class User(DictElement):
    def __init__(self, id, name, message, date):
        """
        Конструктор класса пользователя.

        Параметры:
        - id (int): Идентификатор пользователя.
        - name (str): Имя пользователя.
        - message (str): Сообщение пользователя.
        - date (datetime): Дата сообщения пользователя.
        """
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
        # Вложенный словарь для хранения id региона и количества его упоминаний как города / как района.
        self.regions_count = {}  
        self.region = None
        self.membership = None
        self.user_type = None

    def add_message(self, message):
        """ Добавляет сообщение к существующему списку сообщений пользователя. """
        self.messages += '\n' + message

    def add_dates(self, date):
        """ Добавляет количество сообщений для переданной даты."""
        result = next((messages_date for messages_date in self.messages_dates if messages_date[0] == date), None)
        if result is None:
            self.messages_dates.append((date, 1))
        else:
            date_index = self.messages_dates.index(result)
            self.messages_dates[date_index] = (result[0], result[1] + 1)

    def add_region(self, region_id, region_type):
        """ Добавляет количество упоминаний для указанного региона и типа. """
        region_dict = self.regions_count.get(region_id, {"city": 0, "district": 0})
        if region_type is not None:
            region_dict[region_type] += 1
        self.regions_count[region_id] = region_dict

    def add_messages_count(self):
        """ Увеличивает счетчик сообщений. """
        self.messages_count += 1

    def display_info(self):
        """ Отображает информацию о пользователе в консоли. """
        print(f"Name: {self.name}")
        print(f"ID: {self.id}")
        print(f"Message Count: {self.messages_count}")

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

    def get_first_region(self):
        """ Возвращает первый регион в region_counts пользователя. """
        if self.regions_count is not None:
            sorted_regions = sort_dict(self.regions_count)
            for key, value in sorted_regions.items():
                if key is not None:
                    return key, value
        return None, None
    
    def set_region(self):
        """ Устанавливает регион пользователя на основе количества упоминаний города и района. """
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
        """ Возвращает количество сообщений за последнее указанное количество дней. """
        if self.messages_dates is not None:
            messages_count = 0
            for date, count in reversed(self.messages_dates):
                if date < (datetime.now() - timedelta(days = last_days)).date():
                    break
                messages_count += count
            return messages_count
        
    def get_date_distribution(self, start_year, end_year):
        """ Возвращает распределение количества сообщений (list) по датам за указанные года. """
        if self.messages_dates is not None:
            
            # Создание массива с 12 * 'количество лет' элементами.
            date_distribution = []
            date_distribution.extend([0] * ((end_year - start_year + 1) * 12))

            # Подсчет сообщений по месяцам
            for date, count in self.messages_dates:
                if date.year >= start_year:
                    date_distribution[(date.year - start_year) * 12 + date.month - 1] += count
            return date_distribution
        
    def get_type(self):
        """ Возвращает тип пользователя. """
        for group in group_list:
            if self.name in group.members:
                self.user_type = group.name
            if self.user_type is None:
                self.user_type = UserType.OPERATOR.value
        return self.user_type

            
def add_or_update_user(users_list, name, id, message = None, date = None, region_id = None, region_type = None, membership = None):
    """ Добавляет пользователя в список пользователей или обновляет данные существующего. """
    existing_user = next((user for user in users_list if user.id == id), None)
    if existing_user:
        # Если пользователь уже существует.
        existing_user.add_message(message)
        existing_user.add_region(region_id, region_type)
        existing_user.add_messages_count()
        existing_user.add_dates(date)
        existing_user.membership = membership
    else:
        # Создание нового пользователя и добавление его в список пользователей.
        new_user = User(id, name, message, date)
        if region_id is not None and region_type is not None:
            new_user.add_region(region_id, region_type)
        new_user.membership = membership
        users_list.append(new_user)

def get_user(id):
    """ Возвращает пользователя по его идентификатору. """
    for user in users_list:
        if id in user.id:
            return user
                
users_list = [] # Список пользователей


def sort_dict(dictionary):
    """ Сортирует словарь по сумме его упоминаний в виде района и города. """
    if dictionary is not None:
        return dict(sorted(dictionary.items(), key=lambda item: sum(item[1].values()), reverse=True))


# Перечисление возможных типов пользователей для создания групп.
class UserType(Enum):
    ADMIN = 'Админ'
    OPERATOR = 'Оператор'
    BOT = 'Бот'


group_list = []

class Group():
    """ Группы пользователей по типу. """
    def __init__(self, name):
        self.name = name
        self.members = []
        self.members_count = 0
        group_list.append(self)

    def add_member(self, member):
        self.members.append(member)
        self.members_count += 1

# Добавление пользователей в группы.
admins_group = Group(UserType.ADMIN.value)
admins_group.members = ['Михаил Хабаров', 'Иван Борисов', 'ООО "СИБ" Иркутск Евгений', '112 Иркутская область']

bots_group = Group(UserType.BOT.value)
bots_group.members = ['ms.rt.ru', 'Combot', 'ChatKeeperBot']


class Region(DictElement):
    """ Класс региона, используемый для добавления заголовков для пользователей региона. """
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
        """ Получение суммы сообщений пользователей региона. """
        messages_count = 0
        for user in self.users:
            messages_count += user.messages_count
        return messages_count
    
    def get_last_dates_count(self, days):
        """ Получение суммы сообщений пользователей региона за последние дни. """
        messages_count = 0
        for user in self.users:
            messages_count += user.get_last_dates_count(days)
        return messages_count

    def display_info(self):
        print(f"Name: {self.name}")
        print(f"ID: {self.id}")
        print(f"Message Count: {self.get_messages_count()}")
        print(f"Users count: {self.users_count}")
        print(f"Type: {self.region_type}")
        print("-" * 10)

        
regions_list = [] # Список регионов.

def fill_regions_list():
    """ Заполняет список регионов городами и районами из regions. """
    for region in regions:
        name = region.get("name_city", 0)
        if name:
            region_type = "Город"
            Region(name, region_type)

        name = region.get("name_district", 0)
        if name:
            region_type = "Район (ГО)"
            Region(name, region_type)

# Словарь для поиска региона по корню (match) и вывода соответствующего названия города (name_city) или района (name_district).
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
    { 'match': [ 'Катангск' ], 'name_district': 'Катангский район' },
    { 'match': [], 'name_district': 'Регион не найден' }
]


region_endings = [ 'ий', 'ого', 'ому', 'им', 'ом' ]     

def check_ending(str, ending):
    """ Ищет окончания в переданном слове для определения региона как района. """
    last_letters = str[-len(ending):]
    return last_letters == ending


def find_region_mention(text):
    """ Находит упоминание региона в тексте по массиву поисковых слов match. """

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


messages = []

class Message(DictElement):
    def __init__(self, id, text, date, user_id):
        self.id = id
        self.text = text
        self.lenght = len(text)
        self.words = self.get_words()
        self.words_count = len(self.words)
        self.date = date
        self.user_id = user_id
    
    def get_words(self):
        """ Возвращает список слов в тексте сообщения. """
        if self.text is not None:
            words = re.findall(r'\b\w+\b', self.text)
            words = [word.lower() for word in words]
            return words
        
def open_json(file_path):
    """ Открывает файл формата JSON. """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return None
    return data


writer = None   # Содержит объект writer для записи данных в Excel.

def write_to_excel(df, workbook_path, worksheet_name = 'Sheet1', indexColumn=False):
    """ Записывает DataFrame в файл Excel. """
    global writer
    if writer is None:
        new_writer = pd.ExcelWriter(workbook_path, engine='xlsxwriter')
        writer = new_writer
    elif writer._path == workbook_path:
        new_writer = pd.ExcelWriter(workbook_path, engine='xlsxwriter')
        writer = new_writer
    df.to_excel(writer, worksheet_name, index=indexColumn)    


def parse_data():
    """ 
    Парсит исходные данные из файлов формата JSON. 

    - Заполняет список пользователей, сообщений;
    - Выполняет поиск и назначение региона пользователям;
    - Определяет состоит ли пользователей в группе.
    """

    export_file_path = './docs/result.json'
    users_file_path = './docs/users.json'
    members_file_path = './docs/members.json'
    messages_file_path = './docs/messages.json'

    data = open_json(export_file_path)

    # Получение данных из файла выгрузки сообщений.
    if data is not None:
        for message in data["messages"]:
            if message["type"] != "message":
                continue

            message_id = message["id"]
            user_id = message["from_id"]
            user_name = message["from"]
            date_time  = datetime.strptime(message["date"].replace("T", " "), "%Y-%m-%d %H:%M:%S")
            date = date_time.date()
            text = message["text"]

            if type(text) == list:
                txt_content = ""
                for part in text:
                    if type(part) == str:
                        txt_content += part
                text = txt_content

            text = text.replace("\n", " ")

            # Создание объекта класса Message().
            message = Message(message_id, text, date_time, user_id)
            messages.append(message)

            # Нахождение региона в сообщении пользователя и получение его id и типа.
            region_id, region_type = find_region_mention(text)

            # Добавление/обновление данных пользователя полученными при парсинге данными.
            add_or_update_user(users_list, user_name, user_id, text, date, region_id, region_type)

    members_file_path = './docs/members.json'
    members = open_json(members_file_path)

    # Проверка на наличие пользователя в чате. 
    if members is not None:
        for member in members:
            user = get_user(member["id"])
            if user:
                user.membership = 'Да'
            else:
                add_or_update_user(users_list, member["name"], member["id"], message = None, date = None, membership="Да")
        
        for user in users_list:
            if user.membership is None:
                user.membership = "Нет"

    for user in users_list:
        user.set_region()
        # user.display_info()

    add_users_to_regions()

    # Сохранение списка пользователей и списка сообщений в JSON файлах.
    # TODO: планировалось использовать, чтобы обрабатывать только новые сообщения.
    save_to_json(users_list, users_file_path)
    save_to_json(messages, messages_file_path)


def save_to_json(dict, json_file_path):
    """ Сохраняет значения полей элементов класса DictElement в файл формата JSON. """
    data = [element.to_dict() for element in dict]
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False, default=str)
    

def add_users_to_regions():
    """ Добавление пользователей в список пользователей объекта Region. """

    fill_regions_list()

    for region in regions_list:
        for user in users_list:
            if user.region == region.name:
                region.add_user(user)
            if user.region is None and region.name == "Регион не найден":
                region.add_user(user)

        # region.display_info()


# Правила (value) для выделения ячеек или строки (entire_row) цветом (background-color).
highlight_values = [
    {'value': 'Район (ГО)', 'color': 'background-color: #EEEEEE', 'entire_row': True},  # Серый фон для строки района/города
    {'value': 'Город', 'color': 'background-color: #EEEEEE', 'entire_row': True},
    {'value': 'Админ', 'color': 'color: #666666', 'entire_row': True},
    {'value': 'Бот', 'color': 'color: #666666', 'entire_row': True},
    {'value': 'Удаленный пользователь', 'color': 'background-color: #DD8888', 'entire_row': False},
    {'value': 'Нет', 'color': 'background-color: #DD3333'}
]

def highlight_by_value(row):
    """ Выделение ячеек по заданным правилам highlight_values. """
    for highlight in highlight_values:
        for col, val in row.items():
            if val == highlight['value']:
                if highlight.get('entire_row', False):
                    return [highlight['color'] for _ in row.index]
                else:
                    return [highlight['color'] if v == val else '' for v in row]
    return [''] * len(row.index)


def users_to_excel():    
    """
    Экспорт информации о пользователях и их регионах в Excel.
    
    Создает из полученных при парсинге данных DataFrame'ы (pandas):
    - df_users - пользователи и их активность.
    - df_regions - регионы с агрегированной статистикой (объединяются с пользователями и выступают как заголоки).
    """
    now = datetime.now()
    start_year = 2022
    end_year = now.year
    years = end_year - start_year + 1
    months_columns = [f'{calendar.month_abbr[month + 1]} {year % 100}' for year in range(start_year, end_year + 1) for month in range(12)]

    # Определение столбцов DataFrame для пользователей.
    data_users = {
        "object": [user for user in users_list],
        "ID": [user.id for user in users_list],
        "Имя": [user.name for user in users_list],
        "Сообщений": [user.messages_count if user.messages_count is not None else 0 for user in users_list],
        "Регион": [user.region if user.region else "Ҏегион не найден" for user in users_list],
        "В группе": [user.membership for user in users_list],
        "Тип": [user.get_type() for user in users_list],
        "Актив 14 дн.": [user.get_last_dates_count(14) if user.get_last_dates_count(14) != 0 else '' for user in users_list],
        "Актив 30 дн.": [user.get_last_dates_count(30) if user.get_last_dates_count(30) != 0 else '' for user in users_list],
        "Актив 90 дн.": [user.get_last_dates_count(90) if user.get_last_dates_count(90) != 0 else '' for user in users_list]
    }

    df_users = pd.DataFrame(data_users)

    # Вставка столбцов с распределением сообщений по месяцам для создания гистограмм.
    if start_year > end_year:
        print('Начальная дата распределения сообщений более поздняя, чем конечная.')
    else:
        df_users['date_distribution'] = df_users.apply(lambda row: row['object'].get_date_distribution(start_year, end_year), axis=1)

        # Создание и переименование заголовков для распределения в виде месяц + год.
        df_distribution = pd.DataFrame(df_users['date_distribution'].tolist(), index=df_users.index)
        df_distribution.columns = months_columns

        # Конкатенация распределения сообщений и информации о пользователях и регионах.
        df_users = pd.concat([df_users, df_distribution], axis=1)

        # Начальный столбец для вставки распределения.
        start_column_additional_data = df_users.shape[1] - years * 12

        # Вставка колонок для гистограмм распределения сообщений.
        df_users.insert(start_column_additional_data, '', value=np.nan)
        for year in reversed(range(start_year, end_year + 1)):
            df_users.insert(start_column_additional_data, str(year) + ' г.', value=np.nan)

    # Определение столбцов регионов. Одинаковые столбцы объединяются при конкатенации.
    data_regions = {
        "object": [region for region in regions_list],
        "ID": [None for _ in regions_list],
        "Имя": [region.name for region in regions_list],
        "Сообщений": [0 for _ in regions_list],
        "Регион": [region.name if region.name != "Регион не найден" else "Ҏегион не найден" for region in regions_list],
        "В группе": ['Да' if region.users else 'Нет' for region in regions_list],
        "Тип": [region.region_type for region in regions_list],
        "Актив 14 дн.": [region.get_last_dates_count(14) if region.get_last_dates_count(14) != 0 else '' for region in regions_list],
        "Актив 30 дн.": [region.get_last_dates_count(30) if region.get_last_dates_count(30) != 0 else '' for region in regions_list],
        "Актив 90 дн.": [region.get_last_dates_count(90) if region.get_last_dates_count(90) != 0 else '' for region in regions_list]
    }
    
    df_regions = pd.DataFrame(data_regions)

    # Нахождение суммы сообщений для региона.
    region_messages_sum = df_users.groupby("Регион")["Сообщений"].sum().reset_index()
    df_regions = pd.merge(df_regions, region_messages_sum, on="Регион", how="left", suffixes=('', '_sum'))
    df_regions['Сообщений'] = df_regions['Сообщений_sum'].fillna(df_regions['Сообщений']).astype(int)
    df_regions = df_regions.drop(['Сообщений_sum'], axis=1)
    
    if start_year <= end_year:
        # Нахождение суммы распределения сообщений по месяцам для региона.
        df_regions_sum = df_users.groupby('Регион')[months_columns].sum().reset_index()
        df_regions = pd.merge(df_regions, df_regions_sum, how='left', on='Регион')
        df_users = df_users.drop('date_distribution', axis=1)

    # Сортировка региона для и назначение индексов.
    df_regions = df_regions.sort_values(by=["Регион", "Сообщений"], ascending=[True, False])
    df_regions['ID'] = df_regions.reset_index().index + 1

    # Соединение строк пользователей со строками регионов.
    df = pd.concat([df_users, df_regions], ignore_index=True)

    # Создание категорий с заранее заданной сортировкой.
    sorting_order_type = ["Район (ГО)", "Город", "Оператор", "Админ", "Бот"]
    df['Тип'] = pd.Categorical(df['Тип'], categories=sorting_order_type, ordered=True)
    df = df.sort_values(by=["Регион", "Тип", "Сообщений", "ID"], ascending=[True, True, False, True])

    df = df.drop(['object', "Регион"], axis=1)

    # Назначение стилей к DataFrame.
    # Не используйте styled_df для работы с данными и назначайте стили перед экспортом.
    styled_df = df.style.apply(highlight_by_value, axis=1)

    workbook_path= './docs/Соотнесение пользователей с регионом.xlsx'
    worksheet_name = 'Пользователи и регионы'

    write_to_excel(styled_df, workbook_path, worksheet_name)
    worksheet = writer.book.get_worksheet_by_name(worksheet_name)

    # Добавление гистограмм необходимо выполнять после создания книги.
    if start_year <= end_year:

        # Начальная колонка для гистограмм.
        start_column_sparklines = df.shape[1] - years * 12 - years
        
        for period in range(years):
            for row in range(df.shape[0]):
                target_cell = get_cell_address(row + 1, period + start_column_sparklines - 1) # Ячейка для размещения гистограммы.
                rng = get_range_address(row + 1, start_column_sparklines + years + period * 12, row + 1, start_column_sparklines + years + (period + 1) * 12 - 1) # Диапазон данных.
                worksheet.add_sparkline(target_cell, {'range': rng, 'type': 'column', 'max': 10}) # Добавить гистограмму с указанным типом, шириной и макс. значением.
    else:
        start_column_sparklines = df.shape[1]
        years = 1
    
    add_borders(writer.book, worksheet, 0, 0, df.shape[0], start_column_sparklines + years - 2)
    worksheet.autofit()


def get_cell_address(row, col):
    """ Получение адреса ячейки в формате 'A1'. """
    return Utility.xl_rowcol_to_cell(row, col)

def get_range_address(fitst_row, fitst_col, second_row, second_col):
    """ Получение адреса диапазона в формате 'A1'. """
    return Utility.xl_range(fitst_row, fitst_col, second_row, second_col)

def add_borders(book, worksheet, first_row, first_col, second_row, second_col):
    """ Добавление границ ячеек при помощи условного форматирования. """
    border_format = book.add_format({'border': 1, 'border_color': 'black'})
    rng = get_range_address(first_row, first_col, second_row, second_col)
    worksheet.conditional_format(rng, {'type':'cell', 'criteria': '<>', 'value': -1, 'format': border_format})



# Ключевые слова для поиска инцидентов.
keywords = [
    ["электроэнергия", "электричество", "свет", "ээ", "эл", "э", "отключение"],
    ["сеть", "связь", "соединение"],
    ["авария", "происшествие", "поломка"],
    ["ПК", "АРМ"],
    ["карточки"]
]

mystem = Mystem()

def normalize_words(words):
    """ Нормализация слов с использованием библиотеки pymystem3 """
    lemmas = mystem.lemmatize(words.lower())
    lemmatized_words = [word for word in lemmas if word.isalpha()]
    if len(lemmatized_words) == 1:
        return lemmatized_words[0]
    return lemmatized_words


def word_count(text):
    """ Считает слова в тексте и записывает их в формате {"word1": count1, "word2": count2, ...}. """
    words = re.split(r'\\|/|\n|\. |, |\.| ', text)
    cleared_words = [word for word in words if word.isalpha()]
    word_dict = {}
    for clear_word in cleared_words:
        clear_word = clear_word.lower()
        word_dict[clear_word] = word_dict.get(clear_word, 0) + 1
    return word_dict


def find_word_number(target_word, text):
    """ Возвращает номер слова в тексте или None. """
    try:
        word_number = text.index(target_word)
        return word_number
    except ValueError:
        return None


def find_keyword(keyword, text):
    """ Нахождение ключевого слова в тексте. """

    if len(keyword) > 2:
        nomalized_keyword = normalize_words(keyword)
    else:
        nomalized_keyword = keyword

    normalized_words = normalize_words(text)

    if nomalized_keyword in normalized_words:
        return find_word_number(nomalized_keyword, normalized_words)
    else:
        return -1

# TODO: заменить на распределение инцидентов по дням с указанием пользователя.
def create_pivot_table():
    """ Создание сводной таблицы регион/инцидент """
    
    pivot_table_data = {}

    for i, region in enumerate(regions_list):
        
        show_progress(iteration=i, total=len(regions_list), suffix=region.name)
        
        # Соотнесение имени региона и ключего слова.
        pivot_table_data[region.name] = {", ".join(keyword_set): 0 for keyword_set in keywords}
        all_region_messages = ""
        clear_messages = ""

        # Объединение всех сообщений пользователей из одного региона.
        for user in users_list:
            if user.region == region.name:
                all_region_messages += " " + user.messages

        # Преобразует все сообщения в словарь {"word1": count1, "word2": count2, ...}.
        word_count_dict = word_count(all_region_messages)

        # Составляет очищенное сообщение word1 word2 ...
        # Порядок сохраняется, что позволяет потом найти count1, count2, ...
        for word in word_count_dict.keys():
            clear_messages += " " + word

        # Если ключевое слово есть в тексте, то добавляет его частоту.
        for keyword_set in keywords:
            for keyword in keyword_set:
                position = find_keyword(keyword, clear_messages)
                if position >= 0:
                    pivot_table_data[region.name][", ".join(keyword_set)] += list(word_count_dict.values())[position]

    # Создание DataFrame из словаря.       
    pivot_table_df = pd.DataFrame.from_dict(pivot_table_data, orient="index")

    workbook_path= './docs/Соотнесение пользователей с регионом.xlsx'
    worksheet_name = 'Статистика по проблемам'
 
    write_to_excel(pivot_table_df, workbook_path, worksheet_name, indexColumn=True)  
    worksheet = writer.book.get_worksheet_by_name(worksheet_name)

    add_borders(writer.book, worksheet, 0, 0, pivot_table_df.shape[0], pivot_table_df.shape[1])
    worksheet.autofit()


def get_column_letter(col):
    """ Получить букву столбца Excel на основе его номера. """
    return Utility.xl_col_to_name(col)


def show_progress(iteration, total, prefix='Прогресс:', suffix='', length=50, fill='█'):
    """ Показать прогресса выполнения. Использует текущую итерацию цикла. """
    if total <= 50:
        length = total
    if iteration >= (total - 1):
        percent = 100.0
        bar = fill * length
    else:
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // (total - 1))
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()


def save_close_writer(writer):
    if writer is not None:
        writer._save()
        writer = None


print("Соотнесение пользователя с регионом...")
parse_data()
users_to_excel()
print("Завершено")
print("\nПодсчет количества инцидентов:")
create_pivot_table()
print("\nЗавершено")
save_close_writer(writer)
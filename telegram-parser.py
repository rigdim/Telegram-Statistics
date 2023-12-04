import json
from datetime import datetime
from fuzzywuzzy import fuzz

regions = ["Бадайбо", "Бодайбинское", "Иркут", "Тайшет", "Усолье"]

def normalize_word(word):
    return word.lower()

# Check if normalized word are similar to base word using the Levenshtein distance.
def is_similar_word(word1, word2, threshold=20):
    return fuzz.ratio(normalize_word(word1), normalize_word(word2)) >= threshold

def find_region_mention(text, regions):

    # Split the message into words.
    words = text.split()

    # Check each word for similarity to region names.
    for region in regions:
        for word in words:
            if is_similar_word(word, region):
                return region
    

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

        region = find_region_mention(text, regions)

        print(f"User: {user_name}\n\tMessage: {text}\n\tRegion: {region}\n")


# Call the function to execute the code.
parse_telegram_to_excel()
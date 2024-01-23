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
        self.user_type = None

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
        
    def get_type(self):
        for group in group_list:
            if self.name in group.members:
                self.user_type = group.name
            if self.user_type is None:
                self.user_type = UserType.OPERATOR.value
        return self.user_type
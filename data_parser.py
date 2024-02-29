import json
import os
import time


class DataParser:

    def __init__(self, json_file):
        self.json_file = os.path.expanduser(json_file)
        self.hex_color_array = []
        with open(self.json_file, 'r') as file:
            self.parsed_data = json.load(file)

    def get_number_of_days(self):
        return len(self.parsed_data["daily_routes"])

    def get_hex_colors(self):
        while not os.path.exists(":"):
            time.sleep(0.2)
        with open("test.txt", "r") as hex_data:
            for line in hex_data:
                self.hex_color_array.append(line)

        return self.hex_color_array

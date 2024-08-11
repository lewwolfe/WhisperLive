import logging
import re
import requests
import json

class Minecraft:
    def __init__(self, host="localhost", port=5000):
        self.url = f"http://{host}:{port}/transcript/"
        self.last_words = []
        logging.basicConfig(level=logging.ERROR)

    def send_player_data(self, player_name, data):
        url = self.url + player_name
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                return True
            else:
                logging.error(f"Failed to send data to Minecraft, status code: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Failed to send data to Minecraft, Error: {e}")
            return False

    def clean_and_split(self, s):
        """Remove punctuation and split into words."""
        cleaned_text = re.sub(r'[^\w\s]', '', s)
        return cleaned_text.lower().split()

    def process_data(self, player_name, data):
        latest_entry = data[-1]
        new_text = latest_entry["text"]

        new_words = self.clean_and_split(new_text)
        unique_words = [word for word in new_words if word not in self.last_words]

        self.last_words = new_words
        result = " ".join(unique_words)
        
        if unique_words:
            self.send_player_data(player_name, result)

import os
import json
import requests

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class embedding_wrap(metaclass=Singleton):
    def __init__(self, config_file="ollama_config.json"):
        self.loaded = False
        self.config_data = self.load_config(config_file)
        response = self.load_model(self.config_data["EMBEDDING_MODEL"])
        if response.status_code == 200: self.loaded = True

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        for key, value in config_data.items():
            os.environ[key] = str(value)
            
        return config_data

    def load_model(self, model_name: str):
        url = self.config_data["LOAD_MODEL_API_PATH"]
        payload = {
            "model": model_name,
            "stream": False
        }
        response = requests.post(url, json=payload)

        return response

    def process_input(self, input: str):
        if self.loaded:
            url = self.config_data["EMBEDDING_API_PATH"]
            payload = {
                        "model": self.config_data["EMBEDDING_MODEL"],
                        "input": str(input),
                        "keep_alive": "10m",
                        "options": {
                                    "temperature": self.config_data["EMBED_TEMPERATURE"]
                                    }
                        }
            response = requests.post(url, json=payload, stream=False)
            if response.status_code == 200:
                response_data = response.json()
            else:
                return False
            return response_data["embeddings"]
        else:
            print("Failed to load the model")
            return False


    def run(self, prompt: str, model_name: str = "deepseek-r1:14b-qwen-distill-q4_K_M"):
        return self.process_input(prompt)

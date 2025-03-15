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
        print(self.config_data)
        response = self.load_model(self.config_data["EMBEDDING_MODEL"])
        if response.status_code == 200: self.loaded = True

    def load_config(self, config_file):
        """
        Loads environment-variable-like keys from a JSON file and sets them.
        """
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        for key, value in config_data.items():
            # Ensure everything is a string in the environment.
            os.environ[key] = str(value)
        return config_data

    def load_model(self, model_name: str):
        """
        Instantiates an Ollama client for a given model.
        Because environment variables are already set,
        Ollama respects those concurrency/queue settings.
        """
        url = self.config_data["LOAD_MODEL_API_PATH"]
        payload = {
            "model": model_name,
            "stream": False  # Return a single response instead of a streamed response
        }

        response = requests.post(url, json=payload)
        print("Status code:", response.status_code)
        print("Response:", response.text)

        return response

    def process_input(self, input: str):
        """
        Sends a prompt to the provided Ollama client and prints the 
        streamed output in real-time.
        """
        # client = self.get_client(model_name)
        
        # message = {'role': 'user', 'content': prompt}
        if self.loaded:
            url = self.config_data["EMBEDDING_API_PATH"]
            payload = {
                        "model": self.config_data["EMBEDDING_MODEL"],
                        "input": input,
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
            
            # print(response_data, type(response_data))

            return response_data["embeddings"]
        
        else:
            print("Failed to load the model")


    def run(self, prompt: str, model_name: str = "deepseek-r1:14b-qwen-distill-q4_K_M"):
        """
        Runs the complete workflow: loads config, ensures the model is loaded,
        and processes the prompt.
        """
        return self.process_input(prompt)

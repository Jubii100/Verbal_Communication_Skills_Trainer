import os
import json
import requests
from pydantic import BaseModel

class LLMOutput(BaseModel):
  content: str
  stage: int

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class llm_wrap(metaclass=Singleton):
    def __init__(self, config_file="ollama_config.json"):
        self.loaded = False
        self.config_data = self.load_config(config_file)
        self.load_response = self.load_model(self.config_data["LLM"])
        if self.load_response.status_code == 200: self.loaded = True
        # self.output_schema = LLMOutput.model_json_schema()

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
            "stream": True 
        }

        response = requests.post(url, json=payload)

        return response
    
    def run(self, prompt: str, chat = True):
        return self.process_prompt(prompt, chat)

    def process_prompt(self, prompt: str, chat = True):
        if self.loaded:
            url = self.config_data["CHAT_API_PATH"] if chat else self.config_data["GENERATE_API_PATH"]
            payload = {
                        "model": self.config_data["LLM"],
                        "messages": prompt,
                        # "messages": [
                        #     {
                        #     "role": "user",
                        #     "content": prompt
                        #     }
                        # ],
                        "stream": True,
                        "options": {
                                    "temperature": self.config_data["TEMPERATURE"]
                                    },
                        # "format": self.output_schema
                        }
            response = requests.post(url, json=payload, stream=True)
            complete_message = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:  
                    try:
                        chunk = json.loads(line)
                        complete_message += chunk["message"]["content"]
                        yield complete_message
                    except json.JSONDecodeError as e:
                        print("Could not decode chunk:", line)
                        return False

            # return response
        else:
            print("Failed to load the model")
            return False
import os
import json
import requests

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

    # def get_client(self, model_name: str) -> ollama.Client:
    #     """
    #     Returns the already instantiated client if it exists,
    #     otherwise creates one using the load_model function.
    #     Implements a simple singleton for the client.
    #     """
    #     if self.client is None:
    #         self.client = self.load_model(model_name)
    #     return self.client

    def process_prompt(self, prompt: str, chat = True):
        """
        Sends a prompt to the provided Ollama client and prints the 
        streamed output in real-time.
        """
        # client = self.get_client(model_name)
        
        # message = {'role': 'user', 'content': prompt}
        if self.loaded:
            url = self.config_data["CHAT_API_PATH"] if chat else self.config_data["GENERATE_API_PATH"]
            payload = {
                        "model": self.config_data["LLM"],
                        "messages": [
                            {
                            "role": "user",
                            "content": prompt
                            }
                        ],
                        "stream": True,
                        "options": {
                                    "temperature": self.config_data["TEMPERATURE"]
                                    }
                        }
            response = requests.post(url, json=payload, stream=True)
            self.complete_message = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:  # ignore empty keep-alive lines
                    try:
                        chunk = json.loads(line)
                        # print(chunk, type(chunk))
                        # Process the chunk (for example, print it)
                        # print("Received chunk:")
                        if chunk["done"]:
                            # print("here")
                            # print(self.complete_message)
                            # print(chunk["message"]["content"])
                            return self.complete_message
                        else:
                            self.complete_message += chunk["message"]["content"]
                            # print("here1")
                            # print(self.complete_message)
                            # return chunk["message"]["content"]
                            # print(chunk["message"]["content"])
                            yield self.complete_message
                    except json.JSONDecodeError as e:
                        print("Could not decode chunk:", line)
                        return False

            return response
            # print(f"\nPrompt: {prompt}")
            # for chunk in stream:
            #     token = chunk['message']['content']
            #     print(token, end='', flush=True)
            # print("\n" + "="*50 + "\n")
        else:
            print("Failed to load the model")


    # def run(self, prompt: str, model_name: str = "deepseek-r1:14b-qwen-distill-q4_K_M", chat = True):
    #     """
    #     Runs the complete workflow: loads config, ensures the model is loaded,
    #     and processes the prompt.
    #     """
    #     self.process_prompt(prompt, chat)

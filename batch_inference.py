import os
import ollama
import subprocess
import json
import sys
import requests


with open("ollama_config.json", 'r') as f:
    config_data = json.load(f)

def load_config():
    for key, value in config_data.items():
        os.environ[key] = str(value)


def load_model(model_name: str) -> ollama.Client:

    url = config_data["LOAD_MODEL_API_PATH"]
    payload = {
        "model": config_data["LLM"],
        "stream": False  
    }

    response = requests.post(url, json=payload)

    # print("Status code:", response.status_code)
    # print("Response:", response.text)

    return ollama.Client()


class ClientSingleton:
    _client = None  

    @classmethod
    def get_client(cls, model_name: str) -> ollama.Client:
        if cls._client is None:
            cls._client = load_model(model_name)
        return cls._client


def process_prompt(client: ollama.Client, prompt: str):
    message = {'role': 'user', 'content': prompt}
    stream = client.chat(model=config_data["LLM"], messages=[message], stream=True)
    
    print(f"\nPrompt: {prompt}")
    for chunk in stream:
        token = chunk['message']['content']
        print(token, end='', flush=True)
    print("\n" + "="*50 + "\n") 


def main(prompt):
    load_config()

    client = ClientSingleton.get_client(config_data["LLM"])
    process_prompt(client, prompt)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} \"Your prompt here\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    main(prompt)
import os
import ollama
import subprocess
import json
import sys
import requests


with open("ollama_config.json", 'r') as f:
    config_data = json.load(f)

def load_config():
    """
    Loads environment-variable-like keys from a JSON file and sets them.
    """
    for key, value in config_data.items():
        # Ensure everything is a string in the environment.
        os.environ[key] = str(value)


def load_model(model_name: str) -> ollama.Client:
    """
    Instantiates an Ollama client for a given model.
    Because environment variables are already set,
    Ollama respects those concurrency/queue settings.
    """
    # subprocess.run(["ollama", "pull", model_name], check=True)

    url = config_data["LOAD_MODEL_API_PATH"]
    payload = {
        "model": config_data["LLM"],
        "stream": False  # Return a single response instead of a streamed response
    }

    response = requests.post(url, json=payload)

    # The response should be a JSON object or string.
    print("Status code:", response.status_code)
    print("Response:", response.text)

    return ollama.Client()


class ClientSingleton:
    _client = None  # Class-level variable to store the singleton instance

    @classmethod
    def get_client(cls, model_name: str) -> ollama.Client:
        """
        Returns the already instantiated client if it exists,
        otherwise creates one using the load_model function.
        """
        if cls._client is None:
            cls._client = load_model(model_name)
        return cls._client


def process_prompt(client: ollama.Client, prompt: str):
    """
    Sends a prompt to the provided Ollama client and prints the 
    streamed output in real-time.
    """
    message = {'role': 'user', 'content': prompt}
    stream = client.chat(model=config_data["LLM"], messages=[message], stream=True)
    
    print(f"\nPrompt: {prompt}")
    for chunk in stream:
        token = chunk['message']['content']
        # Adjust the condition to whichever prompts you want to stream in real-time
        # or simply remove it to stream for all prompts:
        # if prompt == "Tell me a brief story about the moon":
        print(token, end='', flush=True)
    print("\n" + "="*50 + "\n")  # Separator between responses


def main(prompt):
    # 1) Load config file to set environment variables
    load_config()

    # 2) Create and load your model *once*, after config is applied
    client = ClientSingleton.get_client(config_data["LLM"])
    process_prompt(client, prompt)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} \"Your prompt here\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    main(prompt)
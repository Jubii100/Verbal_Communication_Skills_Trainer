import sys
# from state_manager import state_manage
from prompt_handler import handle_prompt

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} \"Your prompt here\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    # state_manage(prompt)
    for llm_response in handle_prompt(prompt, chat = True).get_llm_output():
        print(llm_response)
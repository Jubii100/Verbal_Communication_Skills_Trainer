import gradio as gr
from gradio import ChatMessage
from prompt_handler import handle_prompt
import gradio as gr

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ChatInterface(metaclass=SingletonMeta):
    def __init__(self, chat_function):
        self.demo = gr.ChatInterface(
            chat_function,
            title="Verbal Communication Skills Trainer 💪",
            type="messages",
            multimodal=True,
            textbox=gr.MultimodalTextbox(sources=["microphone", "upload"]),
            # additional_inputs= gr.Audio()
        )
        

    def launch_interface(self):
        self.demo.launch()

with open("improptu_speaking.md", "r", encoding="utf-8") as file:
    md_content = file.read()
md_content += "\n"
instructions = {
    "role": "user",
    "content": md_content,
    "metadata": None
}

def think_chat_function(message, history):
    if history: print(type(history[0]))
    history.append(instructions)
    del message["files"]
    message["content"] = message.pop("text")
    message["role"] = "user"
    history.append(message)
    response = [ChatMessage(
        content="",
        metadata={}
    )]

    think_stage = "think"
    llm_handler = handle_prompt()
    llm_generator = llm_handler.get_llm_output(history)
    if llm_generator:
        for llm_response in llm_generator:
            llm_response, think_stage = process_string(llm_response, think_stage)

            if think_stage=="think":
                response[-1].content = llm_response
                response[-1].metadata = {"title": "Thinking", "status": "pending"}
            elif think_stage=="transition":
                response[-1].content = llm_response
                response[-1].metadata["status"] = "done"
                response[-1].metadata["thought_len"] = len(llm_response)
                response.append(ChatMessage(content=""))
            else:
                response[-1]=ChatMessage(content=llm_response[response[-2].metadata["thought_len"]:])
            yield response
        if llm_handler.embedding and llm_handler.embedding not in llm_handler.cache: llm_handler.cache[llm_handler.embedding] = response[-1].content
    else: yield

def process_string(s, think_stage):
    if s.startswith("<think>") and "</think>" not in s: think_stage = "think"
    elif think_stage == "think": think_stage = "transition"
    else: think_stage = "respond"
    
    s = s.replace("<think>", "")
    s = s.replace("</think>", "")
    
    return s, think_stage

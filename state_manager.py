import gradio as gr
from gradio import ChatMessage
from prompt_handler import handle_prompt
import gradio as gr

class StateManage:
    def __init__(self):
        

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ChatInterface(metaclass=SingletonMeta):
    def __init__(self):
        self.demo = gr.ChatInterface(
            chat_function,
            title="Verbal Communication Skills Trainer 💪",
            type="messages",
        )

    def launch_interface(self):
        self.demo.launch()


def chat_function(message, history):
    print(history)
    print("#######################")
    print(message)

    for llm_response in handle_prompt(message, chat = True):
        thinking = False
        if llm_response == '<think>': thinking = True
        elif llm_response == '</think>': thinking = False
        response = ChatMessage(
            content=llm_response,
            metadata={"title": "Evaluating", "id": 0, "status": "pending"} if thinking else {"id": 0, "status": "pending"}
        )
        yield response

    # thoughts = [
    #     "First, I need to understand the core aspects of the query...",
    #     "Now, considering the broader context and implications...",
    #     "Analyzing potential approaches to formulate a comprehensive answer...",
    #     "Finally, structuring the response for clarity and completeness..."
    # ]

    # accumulated_thoughts = ""
    # for thought in thoughts:
    #     accumulated_thoughts += f"- {thought}\n\n"
    #     response.content = accumulated_thoughts.strip()
    #     yield response

    # response.metadata["status"] = "done"
    # yield response

    # response = [
    #     response,
    #     ChatMessage(
    #         content="Based on my thoughts and analysis above, my response is: This dummy repro shows how thoughts of a thinking LLM can be progressively shown before providing its final answer."
    #     )
    # ]
    # yield response

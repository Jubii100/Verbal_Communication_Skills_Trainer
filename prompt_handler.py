from llm_wrapper import llm_wrap
from embedding_wrapper import embedding_wrap
import numpy as np
import hashlib

from collections import OrderedDict

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class handle_prompt(metaclass=Singleton):
    def __init__(self, cache_size = 512):
        self.llm = llm_wrap()
        self.cache = OrderedDict()
        self.cache_size = cache_size

    def get_llm_output(self, prompt, chat = True):
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)

        self.embedding = embedding_wrap().run(prompt)
        if self.embedding: self.embedding = np.array(self.embedding)
        else: self.llm.run(prompt, chat = chat)

        self.embedding = self.process_embedding(self.embedding)
        if self.embedding in self.cache:
            self.cache.move_to_end(self.embedding)
            return [self.cache[self.embedding]]
        
        return self.llm.run(prompt, chat = chat)
    
    def process_embedding(self, embedding: np.ndarray, n_levels: int = 256, min_val: float = None, max_val: float = None) -> np.ndarray:
        if min_val is None:
            min_val = np.min(embedding)
        if max_val is None:
            max_val = np.max(embedding)
        
        if min_val == max_val:
            return np.zeros_like(embedding, dtype=np.uint8)
        
        normalized = (embedding - min_val) / (max_val - min_val)
        quantized_embedding = np.round(normalized * (n_levels - 1)).astype(np.uint8)[0]
        
        return self.hash_np_array(quantized_embedding)
    
    def hash_np_array(self, arr: np.ndarray) -> tuple:
        arr_hash = hashlib.md5(arr.tobytes()).hexdigest()
        return arr_hash
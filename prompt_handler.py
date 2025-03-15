from llm_wrapper import llm_wrap
from embedding_wrapper import embedding_wrap
import numpy as np
import functools

from collections import OrderedDict
cache = OrderedDict()

class handle_prompt:
    def __init__(self, prompt, chat = True):
        self.prompt = prompt
        self.chat = chat
        self.llm = llm_wrap()

        self.embedding = embedding_wrap().run(prompt)
        self.embedding = np.array(self.embedding) if self.embedding else self.embedding
        # print(self.embedding.shape)
        # self.embedding = np.array(embedding_wrap().run(prompt))

        self.llm_output = self.get_llm_output()

    def get_llm_output(self, bits: int = 8, group_size: int = 32):
        """Return LLM output for embedding, using cache to avoid repeat inference."""
        if not isinstance(self.embedding, np.ndarray): return self.llm.process_prompt(self.prompt, chat = self.chat)
        embedding = self.quantize_embedding(self.embedding)
        # return _cached_llm_inference(self.prompt, self.llm, qtuple, bits, group_size)
        return _cached_llm_inference(self.prompt, self.llm, self.chat, embedding)
    
    def quantize_embedding(self, embedding: np.ndarray, n_levels: int = 256, min_val: float = None, max_val: float = None) -> np.ndarray:
        # Determine the quantization range.
        if min_val is None:
            min_val = np.min(embedding)
        if max_val is None:
            max_val = np.max(embedding)
        
        # Avoid division by zero for constant embeddings.
        if min_val == max_val:
            return np.zeros_like(embedding, dtype=np.uint8)
        
        # Normalize the embedding to the [0, 1] range.
        normalized = (embedding - min_val) / (max_val - min_val)
        
        # Scale and round to the desired number of quantization levels.
        quantized_embedding = np.round(normalized * (n_levels - 1)).astype(np.uint8)[0].tolist()#[0]
        # print(quantized_embedding)
        
        return tuple(quantized_embedding)

    # # Example usage:
    # # emb = np.random.rand(128)
    # print(get_llm_output(self.embedding, bits=8))  # First call (cache miss triggers inference)
    # print(get_llm_output(self.embedding, bits=8))  # Second call (cache hit, returns cached result)


def lru_cache_by_key(key_func, maxsize=128):
    """
    Decorator that mimics lru_cache but uses a custom key function.
    The key_func accepts the same arguments as the decorated function
    and returns a hashable cache key.
    """
    
    def decorating_function(user_function):

        @functools.wraps(user_function)
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if key in cache:
                cache.move_to_end(key)  # Mark as recently used
                return cache[key]

            result = user_function(*args, **kwargs)
            cache[key] = result

            if len(cache) > maxsize:
                cache.popitem(last=False)  # Remove least recently used

            return result

        wrapper.cache_clear = cache.clear
        return wrapper

    return decorating_function


@lru_cache_by_key(key_func=lambda prompt, llm, chat, embedding: embedding, maxsize=128)
def _cached_llm_inference(prompt, llm, chat, embedding):
    """Cached LLM inference: returns output for a given quantized embedding."""
    print("Computing inference...")
    print("Embedding:", embedding)
    return llm.process_prompt(prompt, chat=chat)

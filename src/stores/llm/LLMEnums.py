from enum import Enum

class LLMEnums(Enum):
    
    OPENAI = "OPENAI"
    Ollama = "Ollama"
    

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
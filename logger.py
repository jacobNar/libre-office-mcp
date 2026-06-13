import json
from config import AppConfig

class LLMInteractionLogger:
    def __init__(self):
        self.log_path = AppConfig.LOG_FILE_PATH

    def log_interaction(self, role: str, content: str, tool_calls: list = None):
        entry = {
            "role": role,
            "content": content,
        }
        if tool_calls is not None:
            entry["tool_calls"] = tool_calls
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

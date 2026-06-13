import sys
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from server import init_new_draw_document, draw_erd_entity, connect_entities, save_and_export_vsdx
from logger import LLMInteractionLogger
from config import AppConfig

class ERDAgent:
    def __init__(self):
        self.llm = ChatOllama(model=AppConfig.OLLAMA_MODEL)
        self.tools = [init_new_draw_document, draw_erd_entity, connect_entities, save_and_export_vsdx]
        self.system_prompt = "You are an expert database design assistant. Use your tools to create ERD tables and connect them. Arrange them nicely using coordinate offsets so they do not overlap."
        self.agent_executor = create_react_agent(self.llm, tools=self.tools, state_modifier=self.system_prompt)
        self.logger = LLMInteractionLogger()

    def run(self, prompt: str):
        self.logger.log_interaction("system", self.system_prompt)
        self.logger.log_interaction("user", prompt)
        for event in self.agent_executor.stream({"messages": [("user", prompt)]}):
            for node_name, node_state in event.items():
                messages = node_state.get("messages", [])
                for message in messages:
                    message.pretty_print()
                    tool_calls = getattr(message, "tool_calls", None)
                    self.logger.log_interaction(
                        message.type,
                        message.content,
                        tool_calls
                    )

    def start_repl(self):
        while True:
            try:
                prompt = input("ERD Agent> ")
                if not prompt.strip():
                    continue
                if prompt.strip().lower() in ("exit", "quit"):
                    break
                self.run(prompt)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    agent = ERDAgent()
    if len(sys.argv) > 1:
        agent.run(" ".join(sys.argv[1:]))
    else:
        agent.start_repl()

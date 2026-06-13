import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from logger import LLMInteractionLogger
from config import AppConfig

class RemoteERDAgent:
    def __init__(self):
        self.server_url = f"http://{AppConfig.LIBREOFFICE_HOST}:8000/sse"
        self.llm = ChatOllama(model=AppConfig.OLLAMA_MODEL)
        self.system_prompt = "You are an expert database design assistant. Use your tools to create ERD tables and connect them. Arrange them nicely using coordinate offsets so they do not overlap."
        self.logger = LLMInteractionLogger()

    async def run(self, prompt: str):
        self.logger.log_interaction("system", self.system_prompt)
        self.logger.log_interaction("user", prompt)
        
        async with MultiServerMCPClient({
            "libreoffice_draw_erd": {
                "transport": "sse",
                "url": self.server_url
            }
        }) as client:
            tools = await client.get_tools()
            agent_executor = create_react_agent(self.llm, tools=tools, state_modifier=self.system_prompt)
            
            async for chunk in agent_executor.astream({"messages": [("user", prompt)]}):
                for node_name, node_state in chunk.items():
                    messages = node_state.get("messages", [])
                    for message in messages:
                        message.pretty_print()
                        tool_calls = getattr(message, "tool_calls", None)
                        self.logger.log_interaction(
                            message.type,
                            message.content,
                            tool_calls
                        )

async def main():
    agent = RemoteERDAgent()
    prompt = "Initialize a new draw document. Then draw an entity named 'Users' with attributes 'id', 'name', 'email' at coordinates x=3000, y=3000. Draw an entity named 'Orders' with attributes 'id', 'user_id', 'total' at coordinates x=9000, y=6000. Create a one-to-many connector from 'Users' to 'Orders'. Save the result as 'erd_diagram.vsdx'."
    await agent.run(prompt)

if __name__ == "__main__":
    asyncio.run(main())

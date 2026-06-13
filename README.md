# LibreOffice Draw ERD Agent

A local LangGraph ReAct agent connected to a local headless LibreOffice Draw instance via the UNO API, capable of programmatically drawing Database/ER Diagrams (entities and connectors).

---

## Section 1: System Environment & Virtual Environment Setup

Initialize your local Python virtual environment and install dependencies:

```powershell
# 1. Create a virtual environment named .venv
python -m venv .venv

# 2. Activate it on Windows
.venv\Scripts\activate

# 3. Install target dependencies
pip install fastmcp langgraph langchain-ollama langchain-mcp-adapters
```

---

## Section 2: python-uno Environment Configuration

Because the native `uno` module is a compiled C-extension bundled directly with LibreOffice, running `import uno` cleanly inside your virtual environment requires pointing Python to your local LibreOffice program directory.

### Option A: Use the LibreOffice Bundled Python (Recommended / Easiest)
LibreOffice comes with its own Python executable that pre-configures all UNO path bindings. You can execute the script directly using:
```powershell
& "C:\Program Files\LibreOffice\program\python.exe" agent.py
```

### Option B: Link System Python to LibreOffice UNO
1. Set the following environment variables on your PC:
   - `PATH`: Add `C:\Program Files\LibreOffice\program` to your PATH.
   - `URE_BOOTSTRAP`: Set to `vnd.sun.star.pathname:C:\Program Files\LibreOffice\program\fundamentalrc` (or the equivalent path in your installation).
2. Copy `uno.py` and `unohelper.py` from `C:\Program Files\LibreOffice\program` into your `.venv\Lib\site-packages` folder.

---

## Section 3: Codebase Architecture

The codebase is organized into modular classes adhering to DRY, Separation of Concerns, and comment-free style guidelines:

1. [config.py](config.py): Configuration class for connection parameters and models.
2. [logger.py](logger.py): Logs prompts, responses, and tool calls to a local file (`llm_interaction.log`).
3. [libreoffice_client.py](libreoffice_client.py): Class encapsulating UNO client operations (connecting, drawing shapes, linking shapes, and saving).
4. [server.py](server.py): FastMCP server exposing tools using the default `stdio` transport.
5. [agent.py](agent.py): Local LangGraph ReAct agent that binds the tools directly.
6. [remote_agent.py](remote_agent.py): Optional adapter client for remote SSE server connections.

---

## Section 4: Testing & Execution Playbook

### 1. Launch LibreOffice in Headless Listening Mode
Launch LibreOffice locally with a socket listener on port `2002`:

```bash
# On Linux/macOS
sudo soffice "--accept=socket,host=localhost,port=2002;urp;" --headless --norestore --nologo --nodefault

# On Windows
& "C:\Program Files\LibreOffice\program\soffice.exe" "--accept=socket,host=localhost,port=2002;urp;" --headless --norestore --nologo --nodefault
```
*(Make sure the host IP in [config.py](config.py) matches the listener host).*

### 2. Run the Local Agent Orchestrator
Execute the local ReAct agent:

```powershell
python agent.py
```

Provide the agent with database design instructions:
```text
Initialize a new draw document. Then draw an entity named 'Users' with attributes 'id', 'name', 'email' at coordinates x=3000, y=3000. Draw an entity named 'Orders' with attributes 'id', 'user_id', 'total' at coordinates x=9000, y=6000. Create a one-to-many connector from 'Users' to 'Orders'. Save the result as 'erd_diagram.vsdx'.
```

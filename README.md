# LibreOffice Draw ERD Agent

A local LangGraph ReAct agent connected to a remote headless LibreOffice Draw instance over Tailscale, capable of programmatically drawing Database/ER Diagrams (entities and connectors).

---

## Section 1: System Environment & Virtual Environment Setup

Initialize your local Python virtual environment on Windows and install dependencies:

```powershell
# 1. Create a virtual environment named .venv
python -m venv .venv

# 2. Activate it on Windows
.venv\Scripts\activate

# 3. Install target dependencies
pip install fastmcp langgraph langchain-ollama
```

---

## Section 2: Windows python-uno Environment Configuration

Because the native `uno` module is a compiled C-extension bundled directly with LibreOffice, running `import uno` cleanly inside a virtual environment on Windows requires pointing Python to the LibreOffice program directory.

You have two options to run this project:

### Option A: Use the LibreOffice Bundled Python (Recommended / Easiest)
LibreOffice comes with its own Python executable that pre-configures all UNO path bindings. You can execute the script directly using:
```powershell
& "C:\Program Files\LibreOffice\program\python.exe" agent.py
```
*(Make sure to run `pip install fastmcp langgraph langchain-ollama` using the LibreOffice Python first, or add the virtual environment's site-packages to its path).*

### Option B: Link System Python to LibreOffice UNO
1. Set the following environment variables on your Windows PC:
   - `PATH`: Add `C:\Program Files\LibreOffice\program` to your PATH.
   - `URE_BOOTSTRAP`: Set to `vnd.sun.star.pathname:C:\Program Files\LibreOffice\program\fundamentalrc` (or the equivalent path in your installation).
2. Copy `uno.py` and `unohelper.py` from `C:\Program Files\LibreOffice\program` into your `.venv\Lib\site-packages` folder.

---

## Section 3: Codebase Architecture

The codebase is organized into modular classes adhering to DRY, Separation of Concerns, and comment-free style guidelines:

1. [config.py](file:///c:/Users/jdnar/OneDrive/Documents/Repositories/libre-office-mcp/config.py): Configuration class for remote endpoints and models.
2. [logger.py](file:///c:/Users/jdnar/OneDrive/Documents/Repositories/libre-office-mcp/logger.py): Handles logging all prompts, responses, and tool calls to a local file (`llm_interaction.log`) without using heavy libraries.
3. [libreoffice_client.py](file:///c:/Users/jdnar/OneDrive/Documents/Repositories/libre-office-mcp/libreoffice_client.py): Class encapsulating UNO client operations (connecting, drawing shapes, linking shapes, and saving).
4. [server.py](file:///c:/Users/jdnar/OneDrive/Documents/Repositories/libre-office-mcp/server.py): Implements the FastMCP server and declares the tool wrappers.
5. [agent.py](file:///c:/Users/jdnar/OneDrive/Documents/Repositories/libre-office-mcp/agent.py): Instantiates ChatOllama, binds the tools, constructs the ReAct agent, and streams steps to the interactive REPL.

---

## Section 4: Testing & Connectivity Playbook

Follow these steps to establish connectivity and run the agent:

### 1. Launch LibreOffice on the Raspberry Pi
Connect to your Raspberry Pi via SSH and run LibreOffice in headless mode. Bind it to your Pi's Tailscale IP address (e.g., `100.115.120.130`) on port `2002`:

```bash
soffice --headless --accept="socket,host=100.X.Y.Z,port=2002;urp;StarOffice.ComponentContext"
```

### 2. Fast Python Validation Script
Before launching the agent, verify that your local PC can establish a baseline UNO connection to the remote socket. Save the following script to a temporary file (e.g., `test_connection.py`) and run it:

```python
import sys
import uno

def verify_connection():
    try:
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx
        )
        # Replace host with your actual Raspberry Pi Tailscale IP address
        connection_string = "uno:socket,host=100.X.Y.Z,port=2002;urp;StarOffice.ComponentContext"
        print(f"Attempting to resolve connection to: {connection_string}")
        ctx = resolver.resolve(connection_string)
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        print("Success! Successfully connected to remote LibreOffice Desktop.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    verify_connection()
```

### 3. Run the Remote Agent on your Windows PC
You can run the agent locally on Windows using `remote_agent.py` which connects to the server running on your Pi over SSE.

First, ensure you have the server running on the Raspberry Pi:
```bash
# On your Raspberry Pi
python server.py
```
This runs the FastMCP server on port 8000 using the SSE transport.

Then, execute the remote agent on your Windows PC:
```powershell
# On your Windows PC
python remote_agent.py
```

Provide the agent with database design instructions. The agent will stream the reasoning logs and call the remote tools on your Raspberry Pi:
```text
Initialize a new draw document. Then draw an entity named 'Users' with attributes 'id', 'name', 'email' at coordinates x=3000, y=3000. Draw an entity named 'Orders' with attributes 'id', 'user_id', 'total' at coordinates x=9000, y=6000. Create a one-to-many connector from 'Users' to 'Orders'. Save the result as 'erd_diagram.vsdx'.
```

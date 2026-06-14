# LibreOffice Draw MCP Server

A Model Context Protocol (MCP) server that connects to a local headless LibreOffice Draw instance via the UNO API, exposing tools to programmatically draw Database/ER Diagrams (entities and sticky connectors).

---

## Section 1: System Environment & Virtual Environment Setup

Choose the installation track matching your operating system:

### On Linux (Ubuntu/Debian)
1. Install system-level python-uno bindings:
   ```bash
   sudo apt update
   sudo apt install python3-uno
   ```
2. Create your virtual environment with global system packages enabled so it can load the `uno` module:
   ```bash
   python3 -m venv --system-site-packages .venv
   ```
3. Activate the environment:
   ```bash
   source .venv/bin/activate
   ```
4. Install python dependencies:
   ```bash
   pip install fastmcp
   ```

### On Windows
1. Create a standard virtual environment:
   ```powershell
   python -m venv .venv
   ```
2. Activate it:
   ```powershell
   .venv\Scripts\activate
   ```
3. Install python dependencies:
   ```powershell
   pip install fastmcp
   ```

---

## Section 2: python-uno Environment Configuration (Windows Only)

Windows does not distribute a system-level python-uno package. To run the server inside your Windows environment:

#### Option A: Use the LibreOffice Bundled Python (Recommended / Easiest)
LibreOffice comes with its own Python executable that pre-configures all UNO path bindings. You can execute the server directly using:
```powershell
& "C:\Program Files\LibreOffice\program\python.exe" server.py
```

#### Option B: Link System Python to LibreOffice UNO
1. Set the following environment variables on your PC:
   - `PATH`: Add `C:\Program Files\LibreOffice\program` to your PATH.
   - `URE_BOOTSTRAP`: Set to `vnd.sun.star.pathname:C:\Program Files\LibreOffice\program\fundamentalrc` (or the equivalent path in your installation).
2. Copy `uno.py` and `unohelper.py` from `C:\Program Files\LibreOffice\program` into your `.venv\Lib\site-packages` folder.

---

## Section 3: Codebase Architecture

The codebase is organized into modular classes adhering to DRY, Separation of Concerns, and comment-free style guidelines:

1. [config.py](config.py): Configuration class for connection parameters and models.
2. [libreoffice_client.py](libreoffice_client.py): Class encapsulating UNO client operations (connecting, drawing shapes, linking shapes, and saving).
3. [server.py](server.py): FastMCP server exposing tools using the default `stdio` transport.

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

### 2. Run the MCP Server
To run the server over a network port using the Server-Sent Events (SSE) transport:

```bash
python server.py
```
*This starts the server process listening on port `8000`. The server endpoint will be available at `http://<host-ip>:8000/sse`.*

### 3. Connect to the MCP Server Remotely
From your other computer on the Tailscale network, you can connect to the running MCP server by pointing your client application to the SSE URL:

```text
http://<Tailscale-IP>:8000/sse
```

For example, you can configure the remote server in your client's configuration file (such as `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "libreoffice-draw": {
      "url": "http://<Tailscale-IP>:8000/sse"
    }
  }
}
```

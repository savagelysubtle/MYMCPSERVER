# How to get a python mcp running using cursor

### **Step-by-Step Guide**

1. **Install Necessary Tools**

   - Ensure Python is installed on your system.
   - Install the required MCP Python SDK using pip:
     ```bash
     pip install mcp
     ```

2. **Build the MCP Server**

   - Create a Python script for your MCP server. For example, a simple addition tool:

     ```python
     from mcp.server import McpServer
     from mcp.transport.stdio import StdioServerTransport

     # Create MCP server
     server = McpServer(name="Calculator", version="1.0.0")

     # Add a tool for addition
     server.tool("add", {"a": int, "b": int}, lambda params: {"result": params["a"] + params["b"]})

     # Connect transport
     transport = StdioServerTransport()
     server.connect(transport)
     ```

   - Save this file as `calculator_mcp.py`.

3. **Run the MCP Server**

   - Start the server using the following command:
     ```bash
     python /path/to/calculator_mcp.py
     ```

4. **Configure Cursor**

   - Open Cursor and navigate to settings:
     - `File → Preferences → Cursor Settings → MCP → Add New Server`.
   - Fill in the server details:
     - **Name**: Choose a name (e.g., "Calculator").
     - **Type**: Command.
     - **Command**: Provide the full path to your Python script:
       ```bash
       /path/to/your/python /path/to/calculator_mcp.py
       ```
   - Save the configuration and ensure the server indicator turns green.

5. **Test the MCP Server**
   - Open Composer in Cursor and test the integration by typing commands like:
     ```plaintext
     Can you add two numbers 3, 6?
     ```
   - Verify that the MCP server responds correctly.

---

### **Alternative Setup Using MCP Proxy**

If you encounter issues running Python-based servers directly, you can use `mcp-proxy` as an intermediary:

1. Install `uv` and `mcp-proxy`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv tool install mcp-proxy
   ```
2. Run the proxy with your Python script:
   ```bash
   mcp-proxy --sse-port 7070 --pass-environment python -- /path/to/calculator_mcp.py
   ```
3. Configure Cursor to connect to the proxy:
   - Add an SSE MCP server with URL: `http://localhost:7070/sse`.

This method bridges any compatibility gaps between your Python script and Cursor[1][6].

Citations:
[1] https://forum.cursor.com/t/running-non-docker-mcp-servers-in-cursor-a-simple-workaround/64234
[2] https://forum.cursor.com/t/does-the-mcp-sdk-work-with-cursor/52967
[3] https://dev.to/composiodev/how-to-connect-cursor-to-100-mcp-servers-within-minutes-3h74
[4] https://www.youtube.com/watch?v=IFrSOi1geVk
[5] https://forum.cursor.com/t/how-to-use-mcp-server/50064
[6] https://composio.dev/blog/mcp-server-step-by-step-guide-to-building-from-scrtch/
[7] https://www.reddit.com/r/cursor/comments/1ii0ixu/tutorial_the_missing_cursor_mcp_manual/
[8] https://www.youtube.com/watch?v=brhs5DogIf8

---

Answer from Perplexity: pplx.ai/share

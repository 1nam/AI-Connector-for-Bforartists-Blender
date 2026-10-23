# AI-Connector-for-Bforartists-Blender

# AI Connector for Bforartists & Blender

**AI Connector** is a lightweight add-on for **Bforartists 2** and **Blender 2.93** that bridges your 3D workspace with an external AI API. It sends your natural language prompts to a server, retrieves dynamically generated Python code, and runs it instantly inside your 3D view.

## 🚀 Features

*   **Prompt to Action:** Enter text commands (e.g., *"Create a step setup of 5 cubes stacked cleanly layout style"*) to manipulate scenes instantly.
*   **External API Integration:** Connects seamlessly via POST requests to any local or remote AI endpoint (e.g., standard Flask/FastAPI setups hosting LLMs).
*   **Flexible Server Response Parsing:** Accepts direct raw Python code text or structured JSON payloads (looking for `code` or `script` parameters).
*   **Asynchronous Status Monitoring:** Viewport sidebar updates status alerts in real time (`Contacting AI...`, `Executing generated code...`, `Success!`).
*   **Fail-Safe Architecture:** Built-in 15-second network timeout prevents the Bforartists interface from hanging indefinitely during server delays.

## 🛠️ Installation

1.  Download the [ai_connector.py](ai_connector.py) file from this repository.
2.  Open **Bforartists** or **Blender (v2.93)**.
3.  Go to **Edit** > **Preferences** > **Add-ons**.
4.  Click **Install...** at the top right of the preferences window.
5.  Select your downloaded `ai_connector.py` file and click **Install Add-on**.
6.  Search for **"AI Connector"** in the list and check the box to **Enable** it.

## 📖 How to Use

1.  Open the **3D Viewport**.
2.  Press `N` on your keyboard to open the Sidebar panel and click on the **AI Tool** tab.
3.  Under **Server Target Settings**, configure your server endpoint URL (Defaults to `http://localhost:5000/generate`).
4.  Type your description in the **AI Text Prompt** box.
5.  Click the prominent **Ask AI & Run** button to generate and execute your 3D script!

## 🌐 Expected API Payload Details

The add-on communicates using standard HTTP POST requests. 

### Sent Payload:
```json
{
  "prompt": "Your custom text instructions here"
}
```

### Accepted Server Responses:
The add-on will auto-detect and unpack your response string safely if it matches either of these formats:
*   **JSON Payload:** `{"code": "print('Hello World')"}` or `{"script": "..."}`
*   **Raw Response:** A plaintext string containing pure Python code directly.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

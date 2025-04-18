# GDS-Lucknow MUN 2025 Delegate Affairs System

A Streamlit-based application to manage delegate outreach and tracking for the Global Diplomatic Summit-Lucknow MUN 2025.

## Features

- Secure login with optional "Remember Me" cookie-based authentication.
- 📧 **Cold Email Generator**: 
  - Use a built-in template or customize your own.
  - Generate personalized invitation emails using Ollama or GROQ AI models.
  - Copy messages to clipboard or export for further editing.
- 👥 **Delegate Management**:
  - Add, search, filter, and edit delegate details (name, contact info, response status, follow-up dates).
  - Inline data editor with dynamic row operations.
  - Export current delegate list as CSV for offline review.

## Getting Started

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com) running locally with the `gemma3:4b` model, if using Ollama personalization.
- GROQ API key configured in `.env` (if Ollama is unavailable).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/GDS_automations.git
   cd GDS_automations
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with the following variables:
   ```env
   USER_NAME='usrnm'
   USER_PASSWORD=G'pswd'
   SECRET_KEY=your-secret-key
   GROQ_API_KEY=your-groq-api-key  # Only needed if Ollama is not available
   ```
   **Note:** The values above are placeholders. Never commit your real credentials. Ensure that your `.env` file is added to `.gitignore` and kept out of version control.

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

- Open your browser at `http://localhost:8501`.
- Log in with the credentials defined in `.env` (or use defaults).
- Navigate between **Cold Email Generator** and **Delegate Management** from the home page.

## Project Structure

```
├── app.py               # Main Streamlit application
├── backend/             # AI personalization backend logic
│   └── backend.py       # Message generation via Ollama or GROQ
├── delegates.csv        # Persistent storage for delegate records
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
```

## Configuration

- **Authentication**: Uses HMAC-signed cookies and session state for persisted login.
- **AI Models**: `ollama` and `groq` Python clients are used to generate personalized emails. Ollama is preferred when available.
- **Email Templates**: A base template is provided and can be edited directly in the UI.

## Contributing

1. Fork the repo and create a new branch for your feature:
   ```bash
git checkout -b feature/YourFeature
```
2. Make your changes, commit, and push:
   ```bash
git commit -am "Add your feature"
   git push origin feature/YourFeature
   ```
3. Open a Pull Request describing your changes.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

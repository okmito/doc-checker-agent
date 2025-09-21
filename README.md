Smart Doc Checker Agent
Eliminate document conflicts automatically. This AI-powered agent lets you upload multiple policies, contracts, or guidelines to instantly find and flag contradictions. It provides clear explanations and suggests resolutions to ensure your documentation is consistent and error-free, saving time and preventing disputes.

✨ Features
Multi-Document Upload: Supports uploading 2-3 text or markdown documents at a time.

AI-Powered Contradiction Detection: Leverages a Large Language Model to intelligently scan and compare documents for conflicting information.

Structured Reporting: Generates a clear, easy-to-read report detailing each conflict with explanations and suggested fixes.

Usage Monitoring: Tracks the number of documents analyzed and reports generated, ready for billing integration.

Simple Web Interface: Built with Streamlit for a clean, user-friendly experience.

🛠️ Tech Stack
Backend: FastAPI, Python, Uvicorn

Frontend: Streamlit

AI Engine: Cerebras API (using the llama-3.3-70b model)

Tooling: uv for package management, Git

📂 Project Structure
The project is organized into two main components:

doc-checker-agent/
├── backend/
│   ├── main.py           # FastAPI application, AI logic, API endpoints
│   ├── config.py         # Pydantic settings for configuration
│   ├── .env              # Stores the secret API key (must be created manually)
│   └── requirements.txt  # Python dependencies for the backend
│
└── frontend/
    ├── app.py            # The Streamlit user interface code
    └── requirements.txt  # Python dependencies for the frontend

🚀 Getting Started
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Python 3.11 or later

Git

A Cerebras API Key

1. Clone the Repository
git clone [https://github.com/YOUR_USERNAME/doc-checker-agent.git](https://github.com/YOUR_USERNAME/doc-checker-agent.git)
cd doc-checker-agent

2. Set Up the Environment
We use uv for fast and reliable environment management.

# Create a virtual environment using Python 3.11
uv venv -p python3.11

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

3. Install Dependencies
Install the required packages for both the frontend and backend.

# Install backend dependencies
uv pip install -r backend/requirements.txt

# Install frontend dependencies
uv pip install -r frontend/requirements.txt

4. Configure Your API Key
You need to tell the application what your API key is.

Navigate into the backend directory: cd backend

Create a new file named .env.

Open the .env file and add your Cerebras API key like this:

CEREBRAS_API_KEY="YOUR_API_KEY_HERE"

Navigate back to the root directory: cd ..

🏃‍♀️ How to Run the Application
The application requires two separate terminals to run the backend server and the frontend interface.

1. Start the Backend Server

Open your first terminal, make sure your virtual environment is active, and run:

# Navigate to the backend folder
cd backend

# Start the FastAPI server with Uvicorn
uvicorn main:app --reload

You should see a message that the server is running on http://127.0.0.1:8000.

2. Start the Frontend Application

Open a new terminal, activate the same virtual environment, and run:

# Navigate to the frontend folder
cd frontend

# Run the Streamlit app
streamlit run app.py

This will automatically open the application in a new tab in your web browser. You're all set to start analyzing documents!

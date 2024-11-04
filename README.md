# eCom-Chatbot using LangGraph

## Overview
This project outlines a structured workflow for handling customer queries by routing them through various agents. Verta now uses a PostgreSQL database hosted on SQL Server on Google Cloud Platform (GCP) for storing and retrieving product information. The chatbot includes agents such as a SQL-Agent, which retrieves product details and customer reviews from the PostgreSQL database, and a vectorstore for retrieving additional context from product metadata and user reviews. If these sources do not provide a sufficient answer, Verta generates responses using additional data sources to ensure that customers receive clear, concise, and insightful information.

## Installation and Setup
### Prerequisites

Uses python for package management.

- Python ^3.11
- Required Python packages (listed in requirements.txt)

### Steps

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/eCom-dev5/eCom-Chatbot/tree/dev
    cd eCom-Chatbot
    ```

2. **Install Dependencies:**
    You should first install python to create and activate a virtual environment with dependencies. Then run:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Storing API keys and other secret keys**
    To securely store your API keys and other sensitive information, you should create a `.env` file. 
    Follow these steps:

    ```bash
    # In the root directory of your project, create a new file named `.env`:
    touch .env
    ```
    ```bash
    #Open the `.env` file in your favorite text editor and add your API keys in the following format:
    API_KEY=<your-api-key-here>
    ```
    Cover the following in your .env file: `AIRFLOW_UID`, `LANGCHAIN_API_KEY`, `OPENAI_API_KEY`, `LANGCHAIN_PROJECT`, `HF_TOKEN`, `GROQ_API_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`, `INSTANCE_CONNECTION_NAME`, `GOOGLE_APPLICATION_CREDENTIALS`, `GCS_BUCKET_NAME`, `postgres_conn_string`

4. **Generating a GCP JSON Connection File**
    To generate a JSON connection file for Google Cloud Platform (GCP), follow these steps:
    1. Access Credentials:
        - Navigate to Credentials in the Google Cloud Console.
    2. Create a Service Account:
        - Click on Create Credentials and select Service Account.
    3. Assign a Role:
        - Choose the Viewer role for the Service Account, then click Done.
    4. Generate JSON Key:
        - Locate your newly created Service Account.
        - Click on Keys.
        - Select Add Key, then choose JSON.
        - Save the generated JSON file securely.
    5. Store the JSON File:
        - Place the JSON file in the main directory of your project.

5. **Steps for Setting Up Google Cloud SDK in Your Environment**
    1. Install Google Cloud SDK:
        - Download the SDK based on your operating system:
        - Linux: Use the curl command.
        - Mac: Use curl or brew if you have Homebrew installed.
        - Windows: Download the installer from the Google Cloud website.
        ```bash
        # For Linux/MacOS
        curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-<VERSION>-<OS>.tar.gz
        tar -xf google-cloud-sdk-<VERSION>-<OS>.tar.gz
        ./google-cloud-sdk/install.sh
        ```
    2. Initialize the SDK:
        ```bash
        gcloud init
        ```
    3. Authenticate Google Cloud SDK:
        Set up a service account and download its JSON key file.
        Use the following command to authenticate with this key:
        ```bash
        gcloud auth activate-service-account --key-file=<path-to-your-service-account-key>.json
        ```
    4. Set Environment Variables:
        Define environment variables to streamline interaction with Google Cloud.
        ```bash
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_APPLICATION_CREDENTIALS="<path-to-your-service-account-key>.json"
        ```
    5. Enable Required APIs
        Enable Compute Engine, Cloud-SQL and Cloud SQL Admin APIs
        ```bash
        gcloud services enable <API_NAME>
        ```
    6. Verify Installation:
        Run a few commands to confirm that the SDK is set up correctly:
        ```bash
        gcloud --version
        gcloud config list
        gcloud auth list
        ```
    After setting up google SDK, update the google SDK path in docker-compose.yaml

6. **Run the Code:**
    You can execute the provided scripts directly. For example, to format documents:
    ```bash
    streamlit run src/app.py
    ```

## Directory Structures

### `../src/`
Main folder containing files to run Verta locally as APIs
- `app.py`: This Streamlit file is used to deploy the Verta interface locally, enabling user interaction with the chatbot through a web application.
- `graph.py`: This file defines a state machine with interconnected agents and nodes, using environment variables and conditional routing to handle user inputs and stream responses from agents like metadata or a vectorstore retriever.
- `serve.py`: This file defines a FastAPI application that handles two endpoints (`/invoke` and `/stream`) for interacting with an agent system, allowing users to either receive a direct response or stream the agent's output in real-time.
- `test.py`: This test script evaluates the `/invoke` and `/stream` API endpoints by sending various user inputs and checking the responses for successful interaction and proper streaming functionality.

To run streamlit deployed locally, run:

```sh
streamlit run src/app.py
```

### `../src/utils/`
This is the main folder containing Python files responsible for managing agents, nodes, states, and constants.
- `agents.py`: A Module that contains logic related to handling different agents (such as Metadata, Vectorstore-retrieval, and Supervisor)
- `nodes.py`: A Module that defines and manages the different nodes in the workflow.
- `constant.py`: Stores constant values that are used throughout the project.
- `state.py`: Tracks the state of operations and interactions between agents and nodes.

## How to run the code

- Make sure you have run and initialize the data pipeline from `data-pipeline/`
- Run `app.py` to deploy the Webapp.
- Run `serve.py` to host the APIs.


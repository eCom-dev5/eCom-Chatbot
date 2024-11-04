# eCom-Chatbot using LangGraph

## Overview
This project outlines a structured workflow for handling teacher queries by routing them through various agents, including an SQL-Agent for Math Curriculum-related information, a Vectorstore for retrieving content from PDFs and websites, and Ember for generating responses using additional data sources when needed.

## Directory Structures

### `../ember/`
Main folder containing files to run Ember locally as APIs
- `graph.py`: This file defines a state machine with interconnected agents and nodes, using environment variables and conditional routing to handle user inputs and stream responses from agents like a SQL agent or vector store retriever.
- `serve.py`: This file defines a FastAPI application that handles two endpoints (`/invoke` and `/stream`) for interacting with an agent system, allowing users to either receive a direct response or stream the agent's output in real-time.
- `test.py`: This test script evaluates the `/invoke` and `/stream` API endpoints by sending various user inputs and checking the responses for successful interaction and proper streaming functionality.

To deploy locally, run:
```sh
cd ember/
python serve.py
```

### `../ember/utils/`
This is the main folder containing Python files responsible for managing agents, nodes, states, and constants.
- `agents.py`: A Module that contains logic related to handling different agents (such as SQL-Agent, Vectorstore-retrieval, and Supervisor)
- `nodes.py`: A Module that defines and manages the different nodes in the workflow.
- `constant.py`: Stores constant values that are used throughout the project.
- `state.py`: Tracks the state of operations and interactions between agents and nodes.

### `../ember/utils/agent_utils/`
This sub-folder is dedicated to supporting the SQL-Agent and related operations.
- `sql_agent.py`: A python module containing SQL-Agent graph flow as a separate class
- `tools.py`: A python module containing tool functions that interact with the SQL-Agent to get relevant information.
- `utils.py`: A Python module with utility functions for database interactions, data processing, and assigning readable names to clusters/domains.
- `load_sqldb.py`: A python script that processes standard, cluster, and domain data from the [IM Curriculum json](https://drive.google.com/file/d/1PAJYs9xSe2AnpkbGnw5bh4ZYeckaO8Hp/view) file, updates the information using utility functions, and then saves the processed data to a new JSON file and an SQLite database. 

### `../ember/utils/agent_utils/assets/`
This folder contains the raw [standard_dependencies_json](https://drive.google.com/file/d/1PAJYs9xSe2AnpkbGnw5bh4ZYeckaO8Hp/view) file along with its processed `test.json` counterpart.

### `../ember/utils/agent_utils/database/`
This folder contains the SQlite database containing the processed JSON file.

## Installation and Setup

### Prerequisites

Uses poetry for package management.

- Python ^3.11
- Required Python packages (listed in pyproject.toml)

### Steps

1. **Clone the Repository:**
    ```sh
    git clone <repository_url>
    cd <repository_name>
    ```

2. **Install Dependencies:**
    You should first install poetry to create and activate a virtual environment with dependencies. Then run:
    ```sh
    poetry config virtualenvs.in-project true 
    ```

3. **Run the Code:**
    You can execute the provided scripts directly. For example, to format documents:
    ```sh
    cd ember/
    python serve.py
    ```

## Setup

Install necessary packages:

```bash
pip install langchain_community langchain_openai python-dotenv
```

Make sure you have a `.env` file with the following keys:

```bash
OPENAI_API_KEY=<your_openai_api_key>
LANGCHAIN_PROJECT=<your_name_for_project> # This key is optional, it is also defined in the workflow notebooks
```

## How to run the code

- Make sure you have `utils/agent_utils/assets` folder containing the standard_dependencies_json file.
- Run `utils/agent_utils/load_sqldb.py` file to process the raw json file and create a SQlite Database. 
- Run `serve.py` to host the APIs.

## Describing the Workflow

Here's a graph level picture of the workflow:
![Workflow in graph form](workflow.png)

The workflow is a structured sequence of actions designed to guide the user in interacting with the database through various Agents. It manages decision-making at each step by evaluating the outcomes of previous operations, which are represented as nodes. This entire workflow can be visualized as a graph, where edges define how the agent moves from one task (tool node) to the next. Specifically, in this workflow:

- The workflow begins with `supervisor` node: The supervisor is responsible for managing the query. At this stage, the supervisor evaluates the nature of the query and decides the next steps. The supervisor routes the query to either the **SQL-Agent** (for Math Curriculum-related queries), or the **Vectorstore** (for PDFs and/or website related queries) or proceeds to **generate** for handling other generic queries.
- `SQL-Agent`: If the query is related to the Math Curriculum, the supervisor directs it to the SQL-Agent, which contains all the necessary information related to that curriculum. The SQL-Agent tries to provide a solution based on its stored information.
- `Vectorstore`: If the query is related to content stored in **PDFs or website information**, the supervisor forwards it to the **Vectorstore** (ChromaDB). This retriever searches the vectorstore for relevant information and returns the results to the supervisor.
- After the communication with Agents, the flow moves to `generate` : If the query is either generic or the SQL-Agent fails to provide a satisfactory response or supervisor has enough context from the other agents, the flow moves to the "generate" step. This is likely where **Ember**, takes over to analyze and attempt to answer the query using additional data sources


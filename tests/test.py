import requests
import httpx

API_URL = "http://localhost:80" 

def test_invoke(user_input):
    """
    Test the /invoke endpoint by sending a simple user input and printing the response.
    """
    url = f"{API_URL}/invoke"
    payload = {
        "user_input": user_input,
        "config": {"configurable": {"thread_id": "1"}},
        "log_langfuse": 1,
        "stream_tokens": 1
    }

    try:
        # Make a POST request to the /invoke endpoint
        response = requests.post(url, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            print("Invoke API response:", response.json())
        else:
            print(f"Invoke API failed with status code {response.status_code}")
            print("Error:", response.json())
    except Exception as e:
        print(f"Error during /invoke API test: {str(e)}")


def test_stream(user_input):
    """
    Test the /stream endpoint by sending a user input and streaming the response.
    """
    url = f"{API_URL}/stream"

    payload = {
        "user_input": user_input,
        "config": {"configurable": {"thread_id": "1"}},
        "log_langfuse": 1,
        "stream_tokens": 1
    }


    try:
        # Use httpx to handle streaming response
        with httpx.stream("POST", url, json=payload) as response:
            if response.status_code == 200:
                print("Stream API response:")
                # Iterate over streamed responses
                for line in response.iter_text():
                    if line.strip() == "[DONE]":
                        break  # End of the stream
                    print(line.strip())
            else:
                print(f"Stream API failed with status code {response.status_code}")
                print("Error:", response.text)
    except Exception as e:
        print(f"Error during /stream API test: {str(e)}")


if __name__ == "__main__":
    user_test_queries = [
        """Hey!""",
        # "Hola!",
        # "poo poo",
        # "How do I teach fractions?",
        # "What are common ways of doing it?",
        # "What questions can you help me with?",
        # "what are your sources?",
        # "who are you?",
        # "tell me how to plan a lesson on fractions then on decimals",
        # "What are some assessments I can use to test my class on 6.RP.A.1?",
        # "What are the dependencies of the dependencies of 6.RP.A.1?",
    ]

    for user_input in user_test_queries:
        print(f"Testing /invoke endpoint for: {user_input}")
        test_invoke(user_input)
        
        print(f"Testing /stream endpoint for: {user_input}")
        test_stream(user_input)

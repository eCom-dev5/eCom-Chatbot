from utils.state import MultiAgentState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


def route_question(state):
    source = state['question_type']
    if source.datasource == "Metadata":
        return "Metadata"
    elif source.datasource == "Review-Vectorstore":
        return "Review-Vectorstore"
    elif source.datasource == "FINISH":
        return "FINISH"
    

def final_llm_node(state: MultiAgentState):
    question = state["question"]
    documents = state["documents"]

    model = ChatGroq(model_name="llama-3.1-70b-versatile")
    system_prompt = (
        f'''
        You are Alpha, a highly knowledgeable and efficient chatbot assistant designed to help users with questions related to products.
        Your primary role is to assist users by providing concise, accurate, and insightful responses based on the product information and reviews available to you.
        If you don’t have the necessary information to answer the question, simply say that you don’t know.

        There are two agents working alongside you:
        - Metadata: This agent provides answers related to a product. It has all the information about that product.
        - Review-Vectorstore: This is a FAISS Vectorstore db containing documents related to all the user reviews for one product.
        
        When a User (Shopper) comes to you for help, the question might have first been routed through either the Metadata or the Review-Vectorstore. 

        Your primary objective is to offer clear, concise, and helpful advice to the teacher, ensuring that they receive the most accurate and useful information to support their shopping needs.

        Instructions:
        - Analyze the product information and/or reviews provided.
        - Provide brief, clear, and helpful answers to user queries about the product.
        - Focus on delivering concise and actionable insights to help users make informed decisions.

        The responses from those agents are available to you, and if their answers were incomplete or unsatisfactory, you will find this reflected in the context field. 
        Your job is to analyze their responses, determine if they are adequate, and provide additional guidance or clarification where needed.
        Below is the context from one of the agents:
        '''
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                        ("human", "{input}")
                    ]
                )
    question_answer_chain = qa_prompt | model

    generation = question_answer_chain.invoke({"context": documents, "input": question})

    return {"documents": documents, "question": question, "answer": generation}


def followup_node(state: MultiAgentState):
    documents = state['documents']
    question = state['question']
    answer = state['answer']
    
    model = ChatGroq(model_name="llama-3.1-8b-instant")
    system_prompt = (
        '''
        Given the following:
        User Question: {question}
        Answer: {answer}
        Context: {context}
        Please generate three possible follow-up questions that the user might ask, each on a new line, without any numbering or bullet points. Do not include any explanations—just list the follow-up questions.
        Format them like this:
        question1\nquestion2\nquestion3
        '''
    )       
    follow_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                    ]
                )
    
    followup_chain = follow_prompt | model
    followup = followup_chain.invoke({'question': question, 'answer': answer, 'context': documents[-2:]}) # just consider last two document list 
    followup_questions = followup.content.split('\n')
    
    return {"question": question, "answer": answer, "documents": documents, 'followup_questions': followup_questions}       
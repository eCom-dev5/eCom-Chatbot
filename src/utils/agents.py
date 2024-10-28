from langchain_groq import ChatGroq
from langchain.schema import Document
from constants import MEMBERS, OPTIONS
from langchain_openai import ChatOpenAI
from utils.state import MultiAgentState, RouteQuery
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def supervisor_agent(state: MultiAgentState):
    question = state["question"]
    document = state["documents"]

    system_prompt = (
        '''
        You are an efficient supervisor responsible for overseeing a conversation between the following agents: {members}. 

        If you got response from the Agent (response given below as "Generated Answer from the Agents:"), respond with 'FINISH' to move on to next step. 
        
        Based on the user's request, decide which agent should respond next. Each agent will complete a task and return their result. 
        
        There are two agents working alongside you:
            - Metadata: This agent has all metadata information about that product. 
            - Review-Vectorstore: This is a FAISS Vectorstore db containing documents related to all the user reviews for that product.
        
        If you got unsatisfied response from the Agents (Agent Throwing Errors like: "Metadata: Unable to generate result") ONLY THEN Call an Agent a **MAXIMUM of TWO TIMES** before responding with 'FINISH'.
        Once sufficient information is obtained from the Agents, respond with 'FINISH', after which Alpha, the final assistant, will provide the concluding guidance to the user.
        If the query is generic (Hello, How are you, etc) then route it to Alpha and respond with 'FINISH.' 

        If you got satisfactory response from the Agent (response given above), respond with 'FINISH' to move on to next step. 
        '''
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
            ('system', "Generated Answer from the Agents: {document}"),
            (
                "system",
                "Given the conversation above, who should act next?"
                "Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(OPTIONS), members=", ".join(MEMBERS))


    supervisor_chain = prompt | llm.with_structured_output(RouteQuery)
    
    update_documents = [m for m in document[-5:]] # Delete the previous documents in the memory to save context

    return {'question_type' : supervisor_chain.invoke({"question": question, 'document': document}), 'question': question, 'documents': update_documents}


def metadata_node(state: MultiAgentState):
    meta_llm = ChatGroq(model_name="llama-3.1-8b-instant")

    meta_df = state['meta_data']

    modified_details = meta_df['details'].astype(str).str.replace('{', '[')
    
    # Answer question
    meta_system_prompt =( 
        f'''
        You are a great Data Interpreter and Summarizer. Read the Product Meta Data sent to you and Produce it in 500 words.
        
        Meta Data:
        main_category: {(meta_df.at[0,'main_category'])}
        title: {(meta_df.at[0, 'title'])}
        average_rating: {(meta_df.at[0, 'average_rating'])}
        rating_number: {(meta_df.at[0, 'rating_number'])}
        features: {(meta_df.at[0, 'features'])}
        description: {(meta_df.at[0, 'description'])}
        price: {(meta_df.at[0, 'price'])}
        store: {(meta_df.at[0, 'store'])}
        categories: {(meta_df.at[0, 'categories'])}	
        details: {(modified_details.at[0])}

        Return in a proper format:
        main_category: Same 
        title: Same
        average_rating: Same
        rating_number: Same
        features: Summarize	
        description: Summarize
        price: Same
        store: Same	
        categories: Same	
        details: Same/Summarize where necessary	

        Do not answer any user question, just provide the meta data
        '''
    )

    meta_system_prompt = meta_system_prompt.replace('{', '{{').replace('}', '}}')

    meta_qa_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", meta_system_prompt),
                    ]
                )
    parser = StrOutputParser()
    meta_chain = meta_qa_prompt | meta_llm | parser

    try:
        # Meta Summary
        meta_results = meta_chain.invoke({'input': ''})
        meta_results = Document(page_content=meta_results, metadata={"source": "Metadata"})
        
    except Exception as error:
        print(error)
        content = "Metadata: Unable to generate result"
        meta_results = Document(page_content=content, metadata={"source": "Metadata"})

    return {'documents': [meta_results], "question": state["question"]}


def retrieve(state: MultiAgentState):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    question = state["question"]
    retriever = state["retriever"]

    # Retrieval
    documents = retriever.invoke(question)

    return {"documents": documents, "question": question}



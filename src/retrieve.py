import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

def setup_rag_pipeline():
    """
    Sets up an Advanced History-Aware RAG pipeline.
    Connects to the local database, Groq LLM, and manages chat context.
    """
    db_path = "../data/physics_db"
    
    #  Connect to Database (using the exact same Ollama embeddings)
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma(persist_directory=db_path, embedding_function=embedding_model)
    
    # Configure the retriever to fetch the top 3 most relevant textbook chunks
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    #  Connect to Groq LLaMA 3.1 (Lightning fast)
    llm = ChatGroq(
        temperature=0, 
        model_name="llama-3.1-8b-instant"
    )

    # The "Contextualizer" Prompt
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # This intercepts follow-up questions and rewrites them
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    #  The Final Answer Prompt
    qa_system_prompt = """You are an expert physics tutor for undergraduate students.
    Use the following pieces of retrieved textbook context to answer the user's question.
    
    Rules:
    1. If you don't know the answer based on the context, say "I don't have enough information in my textbooks to answer that."
    2. If the question is NOT about physics, firmly say "I am a physics assistant and cannot answer out-of-scope questions."
    3. Always cite the source of your information at the end of your answer.

    Context: {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Combine everything into one massive conversational chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    # We return the vector_db as well so the frontend can calculate confidence scores!
    return rag_chain, vector_db

# --- Quick Test Function ---
if __name__ == "__main__":
    print("Initializing Advanced RAG Engine...")
    chain, vector_db = setup_rag_pipeline()
    print("✅ Pipeline is fully wired and ready!")
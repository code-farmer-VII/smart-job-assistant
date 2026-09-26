import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from .ingestion.loader import load_documents
from .ingestion.chunker import chunk_documents
from .retrieval.retriever import get_chroma_retriever
from .prompts.interview import INTERVIEW_PREP_PROMPT

def create_rag_pipeline():
    """
    Assembles the RAG pipeline components using LangChain LCEL.
    """
    # 1. Ingestion
    raw_docs = load_documents()
    chunks = chunk_documents(raw_docs)
    
    # 2. Retrieval setup
    retriever = get_chroma_retriever(documents=chunks)
    
    # 3. LLM setup
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set properly in .env")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=api_key,
        temperature=0.7
    )
    
    # 4. Format context helper
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    # 5. Chain assembly using LCEL
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | INTERVIEW_PREP_PROMPT
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def run_interview_prep(user_prompt: str) -> str:
    """
    Runs the RAG pipeline to generate interview prep.
    """
    chain = create_rag_pipeline()
    return chain.invoke(user_prompt)

if __name__ == "__main__":
    import sys
    # Add dummy file to test
    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "knowledge_base", "skills", "test.txt")
    os.makedirs(os.path.dirname(kb_path), exist_ok=True)
    with open(kb_path, "w") as f:
        f.write("I am an advanced TypeScript and Python developer with experience in Next.js and PostgreSQL.")
        
    query = sys.argv[1] if len(sys.argv) > 1 else "Prepare me for this backend interview."
    print(f"Generating interview prep for: '{query}'\n")
    print(run_interview_prep(query))

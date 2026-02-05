from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
import traceback
import os

class RAGService:
    def __init__(self, data_path: str = "ustp_data.txt"):
        self.data_path = data_path
        self.vector_store = None
        self.embeddings = OllamaEmbeddings(model="qwen2.5:1.5b") # Using local Ollama model for embeddings

    def initialize(self):
        """Ingests data and builds the vector store."""
        try:
            if not os.path.exists(self.data_path):
                print(f"Error: Data file {self.data_path} not found.")
                return

            loader = TextLoader(self.data_path)
            documents = loader.load()
            
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(documents)
            
            # Persist directory for Chroma
            persist_directory = "./chroma_db"
            print("    RAG: Ingesting documents...")
            self.vector_store = Chroma.from_documents(
                documents=docs, 
                embedding=self.embeddings,
                persist_directory=persist_directory
            )
            print("    RAG: Vector store created.")
            print("RAG Service Initialized & Data Ingested")
            
        except Exception as e:
            print(f"Failed to initialize RAG Service: {e}")
            traceback.print_exc()

    def query(self, question: str, k: int = 3):
        """Retrieves relevant documents for a query."""
        if not self.vector_store:
            return "Knowledge base not initialized."
            
        try:
            results = self.vector_store.similarity_search(question, k=k)
            return "\n".join([doc.page_content for doc in results])
        except Exception as e:
            print(f"Error querying RAG: {e}")
            return "Error retrieving information."

if __name__ == "__main__":
    # Simple test
    rag = RAGService()
    rag.initialize()
    print("Test Query 'registrar':", rag.query("Where is the registrar?"))

from langchain_chroma import Chroma
from embeddings import get_embeddings

def create_vector_db(chunks, persist_dir="chroma_db"):
    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    vectordb.persist()
    return vectordb
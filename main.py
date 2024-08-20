from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from create_documents import build_documents
from create_relationships import build_relationships
from vectorize import vectorize_documents
from link_chunks import link_chunks
from langchain_community.graphs import Neo4jGraph
import os
from graphRAG import get_retriever, get_model, rag_question

build_documents()
#vectorize_documents()
#link_chunks
build_relationships()

os.environ["NEO4J_URI"] = "neo4j://neo4j:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
graph = Neo4jGraph()
graph.refresh_schema()
print(graph.schema)

app = FastAPI()
retriever = get_retriever()
llm = get_model()
class Message(BaseModel):
        text: str

@app.get("/")
def read_root():
    return {"This": "is a test"}

@app.put("/chat/response")
async def respond(message: Message):
    #return graphRAG(message.text, model, retriever)
    return rag_question(message.text, llm, retriever)
#return retriever.invoke(message.text)

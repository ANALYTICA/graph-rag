import neo4j
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain, RetrievalQA
from langchain_community.graphs import Neo4jGraph
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Neo4jVector
import os

retrieval_query_window = """
  MATCH window=
    (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
  WITH node, score, window as longestWindow 
    ORDER BY length(window) DESC LIMIT 4
  WITH nodes(longestWindow) as chunkList, node, score
    UNWIND chunkList as chunkRows
  WITH collect(chunkRows.text) as textList, node, score
  OPTIONAL MATCH (node)-[r0:PART_OF]->(f0:Form)
  OPTIONAL MATCH (node)-[:PART_OF]->(i1:Instructions)-[r1:INSTRUCTIONS_OF]->(f1:Form)
  OPTIONAL MATCH (node)-[:PART_OF]->(s2:Schedule)-[r2:SCHEDULE_OF]->(f2:Form)
  OPTIONAL MATCH (node)-[:PART_OF]->(i3:Instructions)-[r3:INSTRUCTIONS_OF]->(s3:Schedule)-[r4:SCHEDULE_OF]->(f3:Form)
  WITH node AS node, score AS score,
    CASE
    WHEN count(r0)>0 THEN collect('The following is an excerpt from ' + f0.name + ':\n'  +  apoc.text.join(textList, " \n "))
    WHEN count(r1)>0 THEN collect('The following is an excerpt from the instructions for filling out ' + f1.name + ':\n'  +  apoc.text.join(textList, " \n "))
    WHEN count(r2)>0 THEN collect('The following is an excerpt from ' + s2.name  + ', a schedule of ' + f2.name + ':\n'  +  apoc.text.join(textList, " \n "))
    WHEN count(r3)>0 THEN collect('The following is an excerpt from the instructions for filling out ' + s3.name + ', a schedule of ' + f3.name + ':\n'  +  apoc.text.join(textList, " \n "))
    ELSE collect("error")
    END AS text
  RETURN text[0] AS text, score, node {.source} AS metadata
"""

retrieval_query = """
  MATCH window=
      (:Chunk)-[:NEXT*0..1]->(node)-[:NEXT*0..1]->(:Chunk)
  WITH node, score, window as longestWindow
    ORDER BY length(window) DESC LIMIT 4
  WITH nodes(longestWindow) as chunkList, node, score
    UNWIND chunkList as chunkRows
  WITH collect(chunkRows.text) as textList, node, score
  RETURN apoc.text.join(textList, " \n ") AS text, score, node {.source} AS metadata
"""

#retrieval_query = """
#  RETURN node.text AS text, score, node {.source} AS metadata
#"""


NEO4J_URI = "neo4j://neo4j:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"
VECTOR_INDEX_NAME = 'chunked_text'
VECTOR_NODE_LABEL = 'Chunk'
VECTOR_SOURCE_PROPERTY = 'text'
VECTOR_EMBEDDING_PROPERTY = 'embedding'

vector_store = Neo4jVector.from_existing_graph(
    embedding=HuggingFaceEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name=VECTOR_INDEX_NAME,
    node_label=VECTOR_NODE_LABEL,
    text_node_properties=[VECTOR_SOURCE_PROPERTY],
    embedding_node_property=VECTOR_EMBEDDING_PROPERTY,
    retrieval_query=retrieval_query_window,
    )

vector_store2 = Neo4jVector.from_existing_graph(
    embedding=HuggingFaceEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name=VECTOR_INDEX_NAME,
    node_label=VECTOR_NODE_LABEL,
    text_node_properties=[VECTOR_SOURCE_PROPERTY],
    embedding_node_property=VECTOR_EMBEDDING_PROPERTY,
    retrieval_query=retrieval_query,
    )

#retriever = vector_store.as_retriever(search_kwargs={"k": 4, 'fetch_k': 6, "score_threshold": 0.0})
retriever = vector_store.as_retriever()
simple_retriever = vector_store2.as_retriever()
#print(retriever.invoke("the?"))
#https://python.langchain.com/v0.2/docs/integrations/vectorstores/neo4jvector
#result = vector_store.similarity_search("waht is gross income?", k=4)
#print(result,"\n" ,len(result))
def get_retriever():
    return retriever

model = LlamaCpp(
                model_path="./capybarahermes-2.5-mistral-7b.Q5_K_M.gguf",
                n_ctx=4096,
                temperature=0.0,
                max_tokens=1024,
                #top_p=1,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                verbose=True,  # Verbose is required to pass to the callback manager
                stop=["Question:"]
                )
def get_model():
    return model

def rag_question(question,model,retriever):
    llm = model
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        return_source_documents=True
                                                )
    result = qa_chain({"query": question,"max_tokens": 1024})
    return result

#print(rag_question("What are long term capital gains and losses?", llm, retriever))

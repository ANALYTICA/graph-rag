import neo4j
from langchain_community.graphs import Neo4jGraph
import os
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import GraphCypherQAChain
from neo4j.debug import watch
import langchain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Neo4jVector

langchain.verbose = True
#os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_URI"] = "neo4j://neo4j:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
graph = Neo4jGraph()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
    )

def vectorize(prepend, filename):
    if filename.endswith(".txt"):
        with open("./irs_documents/" + filename) as f:
            data = f.read()
        texts = text_splitter.create_documents([data])
    else:
        loaders = []
        loaders.append(PyPDFLoader("./irs_documents/" + filename))
        docs = []
        docs.extend(loaders[0].load())

        texts =  text_splitter.split_documents(docs)
        #texts = text_splitter.split_documents([PyPDFLoader("./" + filename).load()])
    print(texts[0])

    embeddings_model = HuggingFaceEmbeddings()
    texts = [text.page_content for text in texts]
    embeddings = embeddings_model.embed_documents(texts)
    print(len(embeddings[0]))

    db_chunks = []
    for i in range(len(texts)):
        db_chunks.append({
            'text':texts[i],
            'embedding':embeddings[i],
            'chunkId':prepend + "_" + str(i),
            'sequence':i,
            'source':filename
        })

    merge_query = """ 
        MERGE(mergedChunk:Chunk {chunkId: $chunkParam.chunkId})
        ON CREATE SET 
        mergedChunk.text = $chunkParam.text,
        mergedChunk.embedding = $chunkParam.embedding, 
        mergedChunk.source = $chunkParam.source,
        mergedChunk.sequence = $chunkParam.sequence
        RETURN mergedChunk
        """
    graph.query("""
        CREATE CONSTRAINT unique_chunk IF NOT EXISTS 
            FOR (c:Chunk) REQUIRE c.chunkId IS UNIQUE
            """)

    for i  in range(len(db_chunks)):
        graph.query(merge_query, params={'chunkParam':db_chunks[i]})

def vectorize_documents():
    docs = ["f1120.pdf","f1120sd.pdf","if1120.txt","if1120sd.txt"]
    prepends = ["f1120","f1120sd","if1120","if1120sd"]
    for doc, prepend in zip(docs, prepends):
        vectorize(prepend, doc)
        graph.refresh_schema()
        print(graph.schema)
#vectorize_documents()

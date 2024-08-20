import neo4j
from langchain_community.graphs import Neo4jGraph
import os

#os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_URI"] = "neo4j://neo4j:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
graph = Neo4jGraph()

cypher = """
  MATCH (c:Chunk)
  WHERE c.source = $params.source
  WITH c
    ORDER BY c.sequence ASC
  WITH collect(c) as chunk_list
    CALL apoc.nodes.link(
    chunk_list, 
    "NEXT", 
    {avoidDuplicates: true}
    )
  RETURN size(chunk_list)
  """
sources = [
        {'source':'f1120.pdf'},
        {'source':'f1120sd.pdf'},
        {'source':'if1120.txt'},
        {'source':'if1120sd.txt'}
        ]

def link_chunks():
    for entry  in sources:
        n = graph.query(cypher, params={'params':entry})
        print("Number of chunks linked: ", n)

#graph.refresh_schema()
#print(graph.schema)

import neo4j
from langchain_community.graphs import Neo4jGraph
import os

#os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_URI"] = "neo4j://neo4j:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
graph = Neo4jGraph()

cyphers = [

  """
  MATCH (c:Chunk), (f:Form)
  WHERE c.source = f.source
  MERGE (c)-[newRelationship:PART_OF]->(f)
  RETURN count(newRelationship)
  """,
  """
  MATCH (c:Chunk), (i:Instructions)
  WHERE c.source = i.source
  MERGE (c)-[newRelationship:PART_OF]->(i)
  RETURN count(newRelationship)
  """,
  """
  MATCH (c:Chunk), (s:Schedule)
  WHERE c.source = s.source
  MERGE (c)-[newRelationship:PART_OF]->(s)
  RETURN count(newRelationship)
  """,
  """
  MATCH (f:Form), (s:Schedule)
  WHERE f.name = "Form 1120" AND s.name = "Schedule D"
  MERGE (s)-[newRelationship:SCHEDULE_OF]->(f)
  RETURN count(newRelationship)
  """,
  """
  MATCH (f:Form), (i:Instructions)
  WHERE f.name = "Form 1120" AND i.source = "if1120.txt"
  MERGE (i)-[newRelationship:INSTRUCTIONS_OF]->(f)
  RETURN count(newRelationship)
  """,
  """
  MATCH (s:Schedule), (i:Instructions)
  WHERE s.name = "Schedule D" AND i.source = "if1120sd.txt"
  MERGE (i)-[newRelationship:INSTRUCTIONS_OF]->(s)
  RETURN count(newRelationship)
  """
]

def build_relationships():
    for cypher in cyphers:
        n = graph.query(cypher)
        print("number of new relationships: ", n)
    graph.query("""
      CREATE VECTOR INDEX `chunked_texts` IF NOT EXISTS
      FOR (c:Chunk) ON (c.embedding)
      OPTIONS { indexConfig: {
      `vector.dimensions`: 768,
      `vector.similarity_function`: 'cosine'}}
      """)
    print("vector index created")


#print(n)
#graph.refresh_schema()
#print(graph.schema)

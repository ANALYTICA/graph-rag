import neo4j
from langchain_community.graphs import Neo4jGraph
import os

os.environ["NEO4J_URI"] = "neo4j://neo4j:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
graph = Neo4jGraph()

to_create = [

    """
    MERGE (i:Instructions {instructionsId: 'if1120'})
    ON CREATE 
    SET i.source = 'if1120.txt'
    """,
    """
    MERGE (i:Instructions {instructionsId: 'if1120sd'})
    ON CREATE
    SET i.source = 'if1120sd.txt'
    """,
    """
    MERGE (f:Form {formId: 'f1120'})
    ON CREATE
    SET f.source = 'f1120.pdf'
    SET f.name = 'Form 1120'
    """,
    """
    MERGE (s:Schedule {scheduleId: 'f1120sd'})
    ON CREATE
    SET s.source = 'f1120sd.pdf'
    SET s.name = 'Schedule D'
    """,
]
constraints = [
    """
    CREATE CONSTRAINT unique_instructions IF NOT EXISTS
    FOR (i:Instructions) REQUIRE i.instructionsId IS UNIQUE
    """,
    """
    CREATE CONSTRAINT unique_schedule IF NOT EXISTS
    FOR (s:Schedule) REQUIRE s.scheduleId IS UNIQUE
    """,
    """
    CREATE CONSTRAINT unique_form IF NOT EXISTS
    FOR (f:Form) REQUIRE f.formId IS UNIQUE
    """
]

def build_documents():
    all_qs = to_create + constraints
    for query in all_qs:
        graph.query(query)
    cypher = """
      MATCH (anyInstructions:Instructions)
      RETURN anyInstructions
      """
    print(graph.query(cypher))
    graph.refresh_schema()
    print(graph.schema)


#cypher = """
#  MATCH (anyInstructions:Instructions) 
#  RETURN anyInstructions
#  """
#print(graph.query(cypher))
#cypher = """
#  MATCH (anyForm:Form) 
#  RETURN anyForm
#  """
#print(graph.query(cypher))
#cypher = """
#  MATCH (anySched:Schedule)
#  RETURN anySched
#  """  
#print(graph.query(cypher))

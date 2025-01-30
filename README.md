# AI_Neo4jSpecialist

How to let LLM's do all the hard work with Neo4j?

Here is the solution! Just write or say what you want to have in your Neo4j database.

This is a very basic example. You can make a lot of advanced applications from this starting point.

If you want to add more examples, feel free to create PR's.

### Example

Clear database
```
Enter your query (or 'exit' to quit): clear database
Deletes the database
```


Create rooms ...
```
Enter your query (or 'exit' to quit): "We have two rooms with furniture. Create a digital twin."

Generated Cypher: CREATE (room1:Place {name: 'Room 1'})
CREATE (room2:Place {name: 'Room 2'})
CREATE (furniture1:Expense {item: 'Sofa'})
CREATE (furniture2:Expense {item: 'Table'})
CREATE (room1)-[:HAS_EXPENSE]->(furniture1)
CREATE (room2)-[:HAS_EXPENSE]->(furniture2)

Explanation: 1. The first line creates a node labeled 'Place' representing the first room, named 'Room 1'.
2. The second line creates another node labeled 'Place' for the second room, named 'Room 2'.
3. The third line creates a node labeled 'Expense' for a piece of furniture, specifically a 'Sofa'.
4. The fourth line creates another node labeled 'Expense' for a different piece of furniture, a 'Table'.
5. The fifth line creates a relationship of type 'HAS_EXPENSE' from 'Room 1' to the 'Sofa', indicating that this furniture is in the first room.
6. The sixth line establishes a similar relationship from 'Room 2' to the 'Table', indicating that this piece of furniture is in the second room.
Query executed successfully.
Result: []
```

```
Enter your query (or 'exit' to quit): Show nodes with Place label.  
Generated Cypher: MATCH (p:Place) RETURN p
Explanation: The Cypher code starts with the MATCH clause, which is used to specify the pattern we want to find in the graph. Here, we are looking for nodes labeled 'Place'. The 'RETURN' clause then specifies that we want to return the matched nodes, which are represented by the variable 'p'. This query will retrieve all nodes in the database that have the 'Place' label.
Query executed successfully.
Result: [
  {
    "p": {
      "name": "Haus 1"
    }
  },
  {
    "p": {
      "name": "Haus 2"
    }
  },
  {
    "p": {
      "name": "Room 1"
    }
  },
  {
    "p": {
      "name": "Room 2"
    }
  }
]
```
Force clarification query:
```
Enter your query (or 'exit' to quit): do something
Clarification needed: Please provide the specific details of the user query 'do something' so that I can generate the appropriate Cypher code.
Please provide more information: 
```

```
-> "Create an example movie database" 
Set the max_token to a larger value like 10000 (more expensive) for better results.
```

## Setup

In case you have trouble to get it to work:

1. First update requirements.txt to use a compatible PyTorch version:

```txt
neo4j
openai
openai-whisper @ git+https://github.com/openai/whisper.git@main
tiktoken
torch>=2.0.1  # Compatible version for macOS
numpy
requests
tqdm
```

2. Then run this installation command:

```sh
conda create -n ai_env python=3.11
conda activate ai_env
pip install -r requirements.txt --prefer-binary --extra-index-url https://download.pytorch.org/whl/cpu
```


## Start

Console
```sh
% export OPENAI_API_KEY="sk-proj-..."
% python src/openaiNeo4j.py -v -o output.log
```


## Mistakes on installation

### wrong "whisper" installed

https://github.com/openai/whisper/discussions/143


### Neo4j password reset

In case you lost you neo4j password on a Mac with brew:

Here are the steps to reset it to "neo4j#!!"

```sh
% cd /usr/local/var/neo4j/data/dbms

% rm auth

% neo4j-admin dbms set-initial-password neo4j#!!
Changed password for user 'neo4j'. IMPORTANT: this change will only take effect if performed before the database is started for the first time.

% brew services start neo4j
==> Successfully started `neo4j` (label: homebrew.mxcl.neo4j)

brew services info neo4j 
neo4j (homebrew.mxcl.neo4j)
Running: ✔
Loaded: ✔
Schedulable: ✘
User: onk
PID: 223349
```

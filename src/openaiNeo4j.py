# sample call
# python src/openaiNeo4j.py -k YOUR_OPENAI_API_KEY -v -o output.log


import argparse
import json
import logging
import os
import subprocess
import sys
import time
from typing import Dict, Any, Optional

from neo4j import GraphDatabase
from openai import OpenAI

# Konfiguration
DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_PASSWORD = "neo4j###"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_TOKENS = 1000

class Neo4jAssistant:
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, openai_key: str, 
                 model: str, verbose: bool, max_tokens: int, output_file: Optional[str], quiet: bool,
                 timeout: int):
        self.driver = GraphDatabase.driver(
            neo4j_uri, 
            auth=(neo4j_user, neo4j_password),
            connection_timeout=timeout
        )
        self.openai_client = OpenAI(api_key=openai_key)
        self.model = model
        self.verbose = verbose
        self.output_file = output_file
        self.quiet = quiet
        self.max_tokens = max_tokens
        self.db_info = self.get_database_info()

    def get_database_info(self) -> Dict[str, Any]:
        with self.driver.session() as session:
            version = session.run("CALL dbms.components() YIELD name, versions WHERE name = 'Neo4j Kernel' RETURN versions[0] AS version").single()['version']
            schema = session.run("CALL db.schema.visualization()").data()
            stats = session.run("CALL db.stats.retrieve('GRAPH COUNTS')").data()
            indexes = session.run("SHOW INDEXES").data()
            constraints = session.run("SHOW CONSTRAINTS").data()
        return {
            "version": version,
            "schema": schema,
            "stats": stats,
            "indexes": indexes,
            "constraints": constraints
        }

    def process_query(self, query: str) -> Dict[str, Any]:
        prompt = f"""
        You are a Neo4j expert. Interpret the following query and generate the corresponding Cypher code for our Neo4j database (Version {self.db_info['version']}).
        Consider the given database structure and statistics:

        Schema: {json.dumps(self.db_info['schema'])}
        Stats: {json.dumps(self.db_info['stats'])}

        User Query: {query}

        Provide your response in the following JSON format:
        {{
            "clarification": "Optional: Any questions or clarifications needed",
            "cypher": "The Cypher code to execute the query",
            "explanation": "A step-by-step explanation of the Cypher code"
        }}

        If you need more information before generating the Cypher code, only include the "clarification" field in your response.
        If you need no more information don't send the "clarification" field in your response.
        """

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=self.max_tokens
        )

        # self.log(f"Response:\n {response}")

        return json.loads(response.choices[0].message.content)

    def execute_cypher(self, cypher: str) -> Dict[str, Any]:
        try:
            with self.driver.session() as session:
                result = session.run(cypher)
                return {"success": True, "data": result.data()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def neo4j_avail(self) -> Dict[str, Any]:
        return self.execute_cypher("Match () Return 1 Limit 1")
            
    def handle_query(self, query: str):
        response = self.process_query(query)
        
        if "clarification" in response and response["clarification"]:
            self.log(f"Clarification needed: {response['clarification']}")
            clarification = input("Please provide more information: ")
            return self.handle_query(f"{query} {clarification}")

        if "cypher" in response and response["cypher"]:
            self.log(f"Generated Cypher: {response['cypher']}")
            self.log(f"Explanation: {response['explanation']}")
            
            result = self.execute_cypher(response["cypher"])
            if result["success"]:
                self.log("Query executed successfully.")
                self.log(f"Result: {json.dumps(result['data'], indent=2)}")
            else:
                self.log(f"Error executing query: {result['error']}")
                corrected_response = self.process_query(f"The following Cypher query resulted in an error: {response['cypher']}. Error message: {result['error']}. Please correct the query.")
                if "cypher" in corrected_response and corrected_response["cypher"]:
                    self.log(f"Corrected Cypher: {corrected_response['cypher']}")
                    corrected_result = self.execute_cypher(corrected_response["cypher"])
                    if corrected_result["success"]:
                        self.log("Corrected query executed successfully.")
                        self.log(f"Result: {json.dumps(corrected_result['data'], indent=2)}")
                    else:
                        self.log(f"Error executing corrected query: {corrected_result['error']}")
        else:
            self.log("No Cypher query generated.")

    def log(self, message: str):
        # Console output
        if not self.quiet:
            print(message)
        
        # File output
        if self.output_file:
            with open(self.output_file, 'a') as f:
                f.write(f"{message}\n")

    def run(self):
        if ( not self.neo4j_avail() ):
            print("Neo4j Server not running or not available.")
            return
        while True:
            query = input("Enter your query (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            self.handle_query(query)

    def close(self):
        self.driver.close()

def main():
    parser = argparse.ArgumentParser(description="Neo4j Assistant")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress console output")
    parser.add_argument("-k", "--key", 
                        default=os.getenv("OPENAI_API_KEY"),  # Add environment variable fallback
                        help="OpenAI API key (default: $OPENAI_API_KEY)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-o", "--output", help="Output file for logs and data")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout for queries in seconds")
    args = parser.parse_args()

    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)

    neo4j_uri = config.get('neo4j_uri', DEFAULT_NEO4J_URI)
    neo4j_user = config.get('neo4j_user', DEFAULT_NEO4J_USER)
    neo4j_password = config.get('neo4j_password', DEFAULT_NEO4J_PASSWORD)
    openai_model = config.get('openai_model', DEFAULT_OPENAI_MODEL)
    max_tokens = config.get('max_tokens', DEFAULT_MAX_TOKENS)
    timeout = config.get('timeout', args.timeout)

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',  # Add format to avoid duplicate metadata
            handlers=[
                logging.StreamHandler(sys.stdout)  # Single handler for console
            ]
        )


    assistant = Neo4jAssistant(
        neo4j_uri, neo4j_user, neo4j_password, args.key, openai_model,
        args.verbose, max_tokens, args.output, args.quiet, timeout
    )

    try:
        assistant.run()
    finally:
        assistant.close()

if __name__ == "__main__":
    main()

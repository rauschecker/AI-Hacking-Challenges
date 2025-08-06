#!/usr/bin/env python

import asyncio
import websockets
import os
import sqlite3

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
    
def init_db() -> SQLDatabase:
    db_path = "backend/Database.db"
    
    # Only create the database and run SQL if it doesn't already exist
    if not os.path.exists(db_path):
        print("Initializing database from SQL file...")

        # Connect to SQLite and run SQL script
        conn = sqlite3.connect(db_path)
        with open("backend/init.sql", "r") as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()
        conn.close()

    # Return LangChain-compatible SQLDatabase
    return SQLDatabase.from_uri(f"sqlite:///{os.path.abspath(db_path)}")

@tool
def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a) + int(b)

async def chat_with_agent(message: str, model, sql_tools) -> str:
    system_message = SystemMessage(content="""
    Decide if you need to use a tool or not.
    If no tools are suitable, you respond directly. Do not tell the user about your decision.
    You are always funny.
    """)

    messages = [system_message, HumanMessage(content=message)]

    available_functions = {
        'add_two_numbers': add_two_numbers,
        **{tool.name: tool for tool in sql_tools}
    }

    while True:
        response = model.invoke(messages)
        # If tool call is present, handle it
        if response.tool_calls:
        # There may be multiple tool calls in the response
            for tool in response.tool_calls:
        # Ensure the function is available, and then call it
                if function_to_call := available_functions.get(tool['name']):
                    print('Calling function:', tool['name'])
                    print('Arguments:', tool['args'])
                    output = function_to_call.invoke(tool['args'])
                    print('Function output:', output)
                    messages.append(response)    # append the original prompt
                    messages.append(ToolMessage(content=str(output),tool_name=tool['name'], tool_call_id=tool['id']))
                else:
                    print('Function', tool['name'], 'not found')
        
        else:
            # Final response — no more tool calls
            return response.content


# 3. WebSocket handler
async def handler(websocket):
    try:
        # Model with tools bound (just for tool formatting/awareness)
        model = ChatOllama(
            model="llama3.2:3b",
            temperature=0,
            max_tokens=256
        )
        
        sql_tools = SQLDatabaseToolkit(db=init_db(), llm=model).get_tools()
        model_with_tools = model.bind_tools([add_two_numbers, *sql_tools])

        async for message in websocket:
            print("Received message:", message, flush=True)

            # Get agent-like response
            reply = await chat_with_agent(message, model_with_tools, sql_tools)

            await websocket.send(reply)
            await websocket.send("[END]")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

# 4. Main server
async def main():
    print("WebSocket server starting", flush=True)
    async with websockets.serve(
        handler,
        "0.0.0.0",
        int(os.environ.get("PORT", 8090)),
    ):
        print(f"WebSocket server running on port {os.environ.get('PORT', '8090')}", flush=True)
        await asyncio.Future()  # run forever
        init_db()

if __name__ == "__main__":
    asyncio.run(main())

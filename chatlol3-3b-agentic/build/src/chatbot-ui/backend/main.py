#!/usr/bin/env python

import asyncio
import os
import sqlite3
import traceback

import websockets

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit


# ============================================================
# CONFIG
# ============================================================

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8090))

OLLAMA_MODEL = "llama3.2:3b"

# Maximum number of model -> tool -> model cycles
MAX_TOOL_ITERATIONS = 5

# Maximum time allowed for one Ollama call
OLLAMA_TIMEOUT = 60

# Maximum time allowed for a tool call
TOOL_TIMEOUT = 15


# ============================================================
# DATABASE
# ============================================================

def init_db() -> SQLDatabase:
    db_path = "Database.db"

    if not os.path.exists(db_path):
        print("Initializing database from SQL file...", flush=True)

        conn = sqlite3.connect(db_path)

        with open("init.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()

        conn.executescript(sql_script)
        conn.commit()
        conn.close()

        print("Database initialized.", flush=True)

    return SQLDatabase.from_uri(
        f"sqlite:///{os.path.abspath(db_path)}"
    )


# ============================================================
# CUSTOM TOOL
# ============================================================

@tool
def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return int(a) + int(b)


# ============================================================
# AGENT
# ============================================================

async def chat_with_agent(
    message: str,
    model,
    sql_tools,
) -> str:

    print("========================================", flush=True)
    print("Starting agent:", message, flush=True)
    print("========================================", flush=True)

    system_message = SystemMessage(
        content="""
You are a funny assistant.

Answer the user's question directly whenever possible.

Only use a tool when it is genuinely necessary.

For normal conversation, greetings, jokes, opinions, explanations,
and general knowledge questions, DO NOT use SQL tools.

The SQL database should ONLY be used when the user explicitly asks
about information that is stored in the database.

Do not repeatedly call the same tool.

Once you have enough information to answer the user, stop using tools
and provide the final answer.
"""
    )

    messages = [
        system_message,
        HumanMessage(content=message),
    ]

    available_functions = {
        "add_two_numbers": add_two_numbers,
        **{t.name: t for t in sql_tools},
    }

    for iteration in range(1, MAX_TOOL_ITERATIONS + 1):

        print(
            f"[Agent iteration {iteration}/{MAX_TOOL_ITERATIONS}] "
            f"Calling Ollama...",
            flush=True,
        )

        # --------------------------------------------------------
        # Ollama call with HARD timeout
        # --------------------------------------------------------

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    model.invoke,
                    messages,
                ),
                timeout=OLLAMA_TIMEOUT,
            )

        except asyncio.TimeoutError:
            print(
                f"ERROR: Ollama call exceeded {OLLAMA_TIMEOUT} seconds.",
                flush=True,
            )

            return (
                "Sorry, the AI model took too long to respond. "
                "Please try again."
            )

        except Exception as e:
            print("ERROR while calling Ollama:", repr(e), flush=True)
            traceback.print_exc()

            return f"Sorry, the AI model failed: {e}"

        # --------------------------------------------------------
        # Print model response
        # --------------------------------------------------------

        print(
            "Model response received.",
            flush=True,
        )

        print(
            "Model content:",
            repr(response.content),
            flush=True,
        )

        print(
            "Tool calls:",
            response.tool_calls,
            flush=True,
        )

        # --------------------------------------------------------
        # No tools = final answer
        # --------------------------------------------------------

        if not response.tool_calls:

            print(
                "Agent finished without tools.",
                flush=True,
            )

            return response.content

        # --------------------------------------------------------
        # Add assistant message ONCE
        # --------------------------------------------------------

        messages.append(response)

        # --------------------------------------------------------
        # Execute tools
        # --------------------------------------------------------

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            tool_id = tool_call["id"]

            print(
                f"Calling function: {tool_name}",
                flush=True,
            )

            print(
                f"Arguments: {tool_args}",
                flush=True,
            )

            function = available_functions.get(tool_name)

            if function is None:

                print(
                    f"ERROR: Unknown tool: {tool_name}",
                    flush=True,
                )

                messages.append(
                    ToolMessage(
                        content=f"Unknown tool: {tool_name}",
                        tool_name=tool_name,
                        tool_call_id=tool_id,
                    )
                )

                continue

            # ----------------------------------------------------
            # Tool timeout
            # ----------------------------------------------------

            try:

                print(
                    f"Executing {tool_name}...",
                    flush=True,
                )

                output = await asyncio.wait_for(
                    asyncio.to_thread(
                        function.invoke,
                        tool_args,
                    ),
                    timeout=TOOL_TIMEOUT,
                )

                print(
                    f"Function output: {output}",
                    flush=True,
                )

            except asyncio.TimeoutError:

                output = (
                    f"Tool {tool_name} timed out after "
                    f"{TOOL_TIMEOUT} seconds."
                )

                print(
                    "ERROR:",
                    output,
                    flush=True,
                )

            except Exception as e:

                output = f"Tool error: {e}"

                print(
                    "ERROR:",
                    repr(e),
                    flush=True,
                )

                traceback.print_exc()

            messages.append(
                ToolMessage(
                    content=str(output),
                    tool_name=tool_name,
                    tool_call_id=tool_id,
                )
            )

    # ------------------------------------------------------------
    # Too many iterations
    # ------------------------------------------------------------

    print(
        "ERROR: Maximum agent iterations reached.",
        flush=True,
    )

    return (
        "I got stuck thinking about that one. "
        "Please try asking the question another way."
    )


# ============================================================
# WEBSOCKET HANDLER
# ============================================================

async def handler(websocket):

    print(
        "WebSocket client connected.",
        flush=True,
    )

    try:

        async for message in websocket:

            print(
                "Received message:",
                message,
                flush=True,
            )

            try:

                reply = await chat_with_agent(
                    message,
                    MODEL,
                    SQL_TOOLS,
                )

                print(
                    "Sending response:",
                    reply,
                    flush=True,
                )

                await websocket.send(reply)

                await websocket.send("[END]")

                print(
                    "Response sent.",
                    flush=True,
                )

            except Exception as e:

                print(
                    "ERROR processing message:",
                    repr(e),
                    flush=True,
                )

                traceback.print_exc()

                try:
                    await websocket.send(
                        "Sorry, something went wrong."
                    )

                    await websocket.send("[END]")

                except Exception:
                    pass

    except websockets.exceptions.ConnectionClosed:

        print(
            "Client disconnected.",
            flush=True,
        )

    except Exception as e:

        print(
            "WebSocket handler error:",
            repr(e),
            flush=True,
        )

        traceback.print_exc()


# ============================================================
# MAIN
# ============================================================

async def main():

    global MODEL
    global SQL_TOOLS

    print(
        "WebSocket server starting",
        flush=True,
    )

    # ----------------------------------------------------------
    # Initialize database ONCE
    # ----------------------------------------------------------

    db = init_db()

    # ----------------------------------------------------------
    # Initialize Ollama ONCE
    # ----------------------------------------------------------

    print(
        f"Loading Ollama model: {OLLAMA_MODEL}",
        flush=True,
    )

    MODEL_BASE = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0,
        num_predict=256,
    )

    # ----------------------------------------------------------
    # Initialize SQL tools ONCE
    # ----------------------------------------------------------

    print(
        "Creating SQL tools...",
        flush=True,
    )

    SQL_TOOLS = SQLDatabaseToolkit(
        db=db,
        llm=MODEL_BASE,
    ).get_tools()

    print(
        "SQL tools:",
        [t.name for t in SQL_TOOLS],
        flush=True,
    )

    # ----------------------------------------------------------
    # Bind tools
    # ----------------------------------------------------------

    MODEL = MODEL_BASE.bind_tools(
        [
            add_two_numbers,
            *SQL_TOOLS,
        ]
    )

    print(
        "Tools bound to model.",
        flush=True,
    )

    # ----------------------------------------------------------
    # Start websocket server
    # ----------------------------------------------------------

    async with websockets.serve(
        handler,
        HOST,
        PORT,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=5,
    ):

        print(
            f"WebSocket server running on port {PORT}",
            flush=True,
        )

        print(
            "Waiting for connections...",
            flush=True,
        )

        await asyncio.Future()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "\nServer stopped.",
            flush=True,
        )

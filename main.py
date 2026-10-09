
import hashlib

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

EMAIL = "23f3003555@ds.study.iitm.ac.in"


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    message = await request.json()

    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "exam-mcp-server",
                    "version": "1.0.0"
                }
            }
        })

    if method == "notifications/initialized":
        return Response(status_code=202)

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [{
                    "name": "solve_challenge",
                    "description": "Calculate the exam challenge hash.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }]
            }
        })

    if method == "tools/call":
        if params.get("name") != "solve_challenge":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Unknown tool"
                }
            })

        challenge = request.headers.get("x-exam-challenge", "")

        result = hashlib.sha256(
            f"{challenge}:{EMAIL}".encode("utf-8")
        ).hexdigest()[:16]

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": result
                }],
                "isError": False
            }
        })

    if request_id is None:
        return Response(status_code=202)

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    })

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agno.run.team import TeamRunOutput
from agno.utils.pprint import pprint_run_response
from agent import rag_team


load_dotenv()  # loads .env file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("query")

    team_response: TeamRunOutput = rag_team.run(query)
    pprint_run_response(team_response, markdown=True)

    return {"response": team_response}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from agno.agent import Agent
from agno.team import Team

from agno.models.google import Gemini

from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from agno.db.sqlite import SqliteDb

from agno.tools.websearch import WebSearchTools


# Agent DB
agent_db = SqliteDb(db_file="tmp/agents.db")

# Vector DB, Knowledge Base
# -------------------------
# LanceDB Vector DB
vector_db = LanceDb(
    table_name="multi_agent_rag",
    uri="/tmp/lancedb",
    search_type=SearchType.hybrid,
    embedder=GeminiEmbedder(id="gemini-embedding-001"),
)

# Knowledge Base
knowledge = Knowledge(
    vector_db=vector_db,
    # contents_db=agent_db # Store metadata about the contents in the agent database, table_name="agno_knowledge"
)

# Load Documents into the Knowledge Base
knowledge.insert_many(
    urls=[
        "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf",
        "https://docs.agno.com/.md",
        "https://docs.agno.com/agents/overview.md",
        "https://docs.agno.com/teams/overview.md",
        "https://docs.agno.com/knowledge/overview.md",
    ],
    skip_if_exists=True
  )

# Agents
# -------------------------
MODEL = Gemini(id="gemini-3.1-flash-lite")

# Agent 1: Knowledge Retriever
# Sole access to the vector store — searches and returns raw chunks + sources
knowledge_retriever_agent = Agent(
    name="Knowledge Retriever",
    role="Search the vector knowledge base and return relevant chunks with source references",
    model=MODEL,
    knowledge=knowledge,
    search_knowledge=True,   # gives this agent the search_knowledge tool
    instructions=[
        "Search the knowledge base thoroughly for any query you receive.",
        "Always include the source document name or URL for each chunk you return.",
        "If no relevant chunks are found, explicitly say 'NO_KB_RESULTS' so the team knows to use web search.",
        "Do NOT answer the question yourself — return raw retrieved content only.",
    ],
    markdown=True,
)

# Agent 2: Web Search Agent
# Falls back to live web search when the KB has no relevant content
web_search_agent = Agent(
    name="Web Search Agent",
    role="Search the web for current or supplementary information when the knowledge base is insufficient",
    model=MODEL,
    tools=[WebSearchTools()],
    instructions=[
        "You are called ONLY when the Knowledge Retriever returns 'NO_KB_RESULTS' or insufficient content.",
        "Run 2-3 targeted web searches to find the most relevant and recent information.",
        "Always include the source URL for every fact you return.",
        "Return raw search findings — do NOT synthesise a final answer.",
    ],
    markdown=True,
)

# Agent 3: Response Synthesizer
# Takes outputs from Agents 1 & 2 and produces the final cited answer
response_synthesizer_agent = Agent(
    name="Response Synthesizer",
    role="Merge retrieved knowledge and web search results into a clear, cited, well-structured answer",
    model=MODEL,
    instructions=[
        "Synthesise the information provided by your team members into one coherent answer.",
        "Always include a 'Sources' section at the end listing every reference used.",
        "Distinguish clearly between knowledge-base sources and web search sources.",
        "If team members disagree or contradict each other, note the discrepancy.",
        "Format your answer with clear headings, bullet points, and code blocks where appropriate.",
        "Keep the final answer concise — under 400 words unless the query demands more depth.",
    ],
    markdown=True,
)

# Team
# -------------------------
rag_team = Team(
    name="Multi-Agent RAG Team",
    model=MODEL,   # A stronger model can be used for coordinator
    members=[
        knowledge_retriever_agent,
        web_search_agent,
        response_synthesizer_agent,
    ],
    instructions=[
        # ── Routing logic ────────────────────────────────────────────────
        "STEP 1 — Always start by calling 'Knowledge Retriever' with the user's query.",
        "STEP 2 — If Knowledge Retriever returns 'NO_KB_RESULTS', call 'Web Search Agent'.",
        "         If Knowledge Retriever finds relevant content, skip 'Web Search Agent'.",
        "STEP 3 — Always call 'Response Synthesizer' last with the collected results.",
        # ── Quality rules ────────────────────────────────────────────────
        "Never answer directly — always delegate to the appropriate specialist agents.",
        "Ensure every final response contains cited sources.",
    ],
    show_members_responses=True,   # prints each agent's intermediate output
    db=agent_db, # we need to assign a database for add_history_to_context to work
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)
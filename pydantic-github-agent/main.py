from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.agent_endpoint import router as agent_router

app = FastAPI()

app.include_router(agent_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

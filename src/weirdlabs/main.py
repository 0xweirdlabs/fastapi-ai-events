from fastapi import FastAPI
from .routers.alarms import router as alarms_router
from .routers.agent_alarms import router as agent_alarms_router

app = FastAPI(title="Weirdlabs.ai Dual-Mode API")
app.include_router(alarms_router)
app.include_router(agent_alarms_router)

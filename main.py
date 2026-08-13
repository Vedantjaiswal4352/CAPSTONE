import logging
import os
import time
from fastapi import FastAPI,Depends,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from auth import (get_current_user, require_admin, create_access_token, user_db)
from retrieval import initialize_retrieval, execute_query
from models import (LoginRequest, QueryRequest, QueryResponse, HealthResponse, DashboardResponse, TokenResponse, HistoryResponse)
from analytics import (track_request, cache_query, get_cached_query, get_user_history, get_analytics_summary)

# Setting Login
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("capstone_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize retrieval system for app startup"""
    initialize_retrieval()
    logger.info("Application started successfully.")

    # Yield control back to FastAPI
    yield

    """Cleaning up app shutdown"""
    logger.info("Application shutting down...")

app = FastAPI(
    title='Capstone AI Pipeline',
    version='2.0',
    description='Advanced AI Data Pipeline with Auth and monitoring',
    lifespan=lifespan
)

static_dir = os.path.join(os.path.dirname(__file__),"static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir),name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")

#Auth Endpoints
@app.post("/token", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Login endpoint to obtain JWT token (accepts JSON)"""
    user = user_db.get(credentials.username)
    if not user or user["password"] != credentials.password:
        logger.warning(
            f"Failed login attempt for user: {credentials.username}"
        )
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    access_token = create_access_token({
        "sub":credentials.username,
        "role": user["role"]
    })
    logger.info(f"User {credentials.username} logged in successfully.")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"]
    }

# Query Endpoint
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest, user : dict = Depends(get_current_user)):
    """Query endpoint with caching and performance tracking"""
    start_time = time.time()
    cache_key = f"{request.question}:{user['username']}"

    # Checking cache first
    cached_result = get_cached_query(cache_key)
    if cached_result:
        logger.info(f"Cache hit for query: {request.question[:50]}")
        track_request(
            username=user["username"],
            question=request.question,
            response_time=0.001
        )
        return {
            "question": request.question,
            "answer": cached_result["answer"],
            "cached": True,
            "response_time": 0.001,
            "user": user['username']
        }
    try:
        logger.info(f"User {user['username']} asked: {request.question}")
        answer = await execute_query(request.question)

        cache_query(cache_key, answer, user['username'])

        elasped_time = time.time() - start_time
        track_request(
            username=user["username"],
            question=request.question,
            response_time=elasped_time
        )

        return {
            "question": request.question,
            "answer": answer,
            "cached": False,
            "response_time": elasped_time,
            "user": user["username"]
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/history",response_model=HistoryResponse)
async def get_history(user: dict = Depends(get_current_user)):
    """Get query for current user"""
    history = get_user_history(user['username'])
    return {
        "user": user['username'],
        "query_count": len(history),
        "history": history[-10:]
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    analytics = get_analytics_summary()
    return {
        "status": "healthy",
        "query_engine_initialized": True,
        "cached_queries": analytics["cached_queries"]
    }

@app.get("/dashboard", response_model=DashboardResponse)
async def dashboard(user: dict = Depends(get_current_user)):
    """Advanced monitoring dashboard with detailed metrics"""
    analytics = get_analytics_summary()
    return {
        "status": "Pipeline running...",
        "user": user['username'],
        "role": user['role'],
        "total_queries": analytics['total_queries'],
        "total_users": analytics['total_users'],
        "cached_queries": analytics['cached_queries'],
        "avg_response_time": analytics['avg_response_time']
    }

@app.get("/")
async def landing_page():
    """Serve the landing page HTML"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir,"static","index.html")

    logger.info(f"Attempting to serve: {html_file}")
    logger.info(f"File exist: {os.path.exists(html_file)}")

    if os.path.exists(html_file):
        return FileResponse(html_file)
    else:
        logger.error(f"Landing page not found at {html_file}")
        raise HTTPException(status_code=404, detail='Landing page not found.')
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import httpx
from groq import Groq
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
import uuid
import logging
import sys
import time
from asyncio import create_task, gather

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Search and Answer API",
    description="An API that combines web search with Groq LLM for intelligent answers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for keeping track of query results
query_store = {}

class QueryRequest(BaseModel):
    query: str = Field(..., description="The search query to process")
    num_results: Optional[int] = Field(default=5, description="Number of search results to process")

class QueryResponse(BaseModel):
    query_id: str
    status: str
    query: str
    answer: Optional[str] = None
    sources: Optional[List[Dict[str, str]]] = None
    created_at: datetime
    error: Optional[str] = None
    processing_time: Optional[float] = None
    last_updated: datetime

class ContentVerifier:
    """
    Helper class to verify and validate content credibility
    """
    @staticmethod
    def is_credible_domain(url: str) -> bool:
        """
        Check if the domain is from a generally credible source
        """
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            
            # Red flags in URLs
            suspicious_patterns = [
                'free-download',
                'miracle-solution',
                'secret-revealed',
                'one-weird-trick',
                'spam',
                'scam'
            ]
            
            return not any(pattern in domain for pattern in suspicious_patterns)
        except:
            return False
    
    @staticmethod
    def check_content_quality(text: str) -> bool:
        """
        Basic quality checks for content
        """
        if not text or len(text.strip()) < 50:  # Too short
            return False
            
        # Check for spam-like patterns
        spam_patterns = [
            'click here',
            'buy now',
            'limited time offer',
            'act now',
            '100% guaranteed'
        ]
        
        return not any(pattern in text.lower() for pattern in spam_patterns)
    
class WebSearcher:
    def __init__(self, groq_api_key: str = None, serper_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.serper_api_key = serper_api_key or os.getenv("SERPER_API_KEY")
        
        if not self.groq_api_key or not self.serper_api_key:
            raise ValueError("Missing required API keys. Please set GROQ_API_KEY and SERPER_API_KEY in .env file")
        
        logger.info("Initializing WebSearcher with API keys")
        self.groq_client = Groq(api_key=self.groq_api_key)
        self.headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        self.content_verifier = ContentVerifier()
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform a web search using Serper API
        """
        url = "https://google.serper.dev/search"
        payload = {
            'q': query,
            'num': num_results
        }
        
        logger.debug(f"Searching web for query: {query}")
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            results = response.json()
            logger.debug(f"Found {len(results.get('organic', []))} search results")
            return results.get('organic', [])
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            raise

    async def fetch_webpage_content(self, url: str) -> str:
        """
        Fetch and extract main content from a webpage
        """
        logger.debug(f"Fetching content from URL: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(['script', 'style', 'header', 'footer', 'nav']):
                    script.decompose()
                
                # Get text content
                text = soup.get_text(separator='\n', strip=True)
                
                # Basic text cleaning
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = '\n'.join(lines)
                
                logger.debug(f"Successfully extracted {len(text)} characters from {url}")
                return text[:4000]
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return f"Error fetching content: {str(e)}"

    async def process_query(self, user_query: str, num_results: int = 3) -> Dict:
        """
        Process a user query with enhanced verification and fact-checking
        """
        logger.info(f"Processing query: {user_query}")
        try:
            # Search the web
            search_results = self.search_web(user_query, num_results * 2)  # Get more results for filtering
            if not search_results:
                logger.warning("No search results found")
                return {
                    "answer": "I couldn't find any reliable search results for your query.",
                    "sources": []
                }
            
            # Filter and verify sources
            verified_contents = []
            verified_sources = []
            
            for result in search_results:
                if 'link' in result and self.content_verifier.is_credible_domain(result['link']):
                    content = await self.fetch_webpage_content(result['link'])
                    
                    if self.content_verifier.check_content_quality(content):
                        verified_contents.append({
                            'url': result['link'],
                            'title': result.get('title', ''),
                            'content': content
                        })
                        verified_sources.append({
                            'url': result['link'],
                            'title': result.get('title', ''),
                            'snippet': result.get('snippet', '')
                        })
                        
                        if len(verified_contents) >= num_results:
                            break
            
            if not verified_contents:
                return {
                    "answer": "I found some results but couldn't verify their reliability. Please try rephrasing your query.",
                    "sources": []
                }
            
            # Prepare prompt with enhanced verification instructions
            prompt = f"""Based on the following verified web search results, please answer this question: {user_query}

            Instructions:
                1. Analyze information critically and look for consensus among sources
                2. If sources disagree, acknowledge the different viewpoints
                3. If information seems uncertain, express appropriate doubt
                4. Cite specific sources when making claims
                5. Don't make definitive claims about controversial topics

            Search Results:
            """
            
            for idx, content in enumerate(verified_contents, 1):
                prompt += f"\nSource {idx}: {content['title']}\nURL: {content['url']}\n{content['content'][:1000]}\n"
            
            # Two-step verification with Groq
            # First: Generate initial answer
            completion = self.groq_client.chat.completions.create(
                model=os.getenv("GROQ_MODEL"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate, well-sourced answers based on verified web search results. Always maintain a skeptical mindset and acknowledge uncertainties."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            initial_answer = completion.choices[0].message.content
            
            # Second: Verify and refine the answer
            verification_prompt = f"""Please verify and refine this answer, considering:
            1. Are all claims properly supported by the sources?
            2. Are there any logical inconsistencies?
            3. Are uncertainties appropriately acknowledged?
            4. Is the tone appropriately balanced?

            Original Answer:
            {initial_answer}

            Please provide a refined version that addresses any issues found."""

            verification = self.groq_client.chat.completions.create(
                model=os.getenv("GROQ_MODEL"),
                messages=[
                    {"role": "system", "content": "You are a critical fact-checker. Your job is to verify information and ensure accurate, well-balanced responses."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            
            final_answer = verification.choices[0].message.content
            logger.info("Successfully generated and verified answer")
            
            return {
                "answer": final_answer,
                "sources": verified_sources,
                "verification_note": "This response has been verified for accuracy and credibility."
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

class TaskManager:
    def __init__(self):
        self.tasks = {}
        
    async def add_task(self, query_id: str, coro):
        task = create_task(coro)
        self.tasks[query_id] = task
        try:
            await task
        except Exception as e:
            logger.error(f"Task failed for query_id {query_id}: {str(e)}")
        finally:
            del self.tasks[query_id]

task_manager = TaskManager()

# Initialize WebSearcher
try:
    searcher = WebSearcher()
except Exception as e:
    logger.error(f"Failed to initialize WebSearcher: {str(e)}")
    raise

async def process_query_background(query_id: str, query: str, num_results: int):
    logger.info(f"Starting background processing for query_id: {query_id}")
    start_time = time.time()
    
    try:
        # Update status to show processing has started
        query_store[query_id].update({
            "status": "searching",
            "last_updated": datetime.utcnow()
        })
        
        result = await searcher.process_query(query, num_results)
        
        # Log the completion time
        processing_time = time.time() - start_time
        logger.info(f"Query {query_id} completed in {processing_time:.2f} seconds")
        
        query_store[query_id].update({
            "status": "completed",
            "answer": result["answer"],
            "sources": result["sources"],
            "last_updated": datetime.utcnow(),
            "processing_time": processing_time
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing query_id {query_id}: {error_msg}", exc_info=True)
        query_store[query_id].update({
            "status": "failed",
            "error": error_msg,
            "last_updated": datetime.utcnow()
        })

@app.post("/query", response_model=QueryResponse)
async def create_query(query_request: QueryRequest, background_tasks: BackgroundTasks):
    query_id = str(uuid.uuid4())
    logger.info(f"Received new query. ID: {query_id}, Query: {query_request.query}")
    
    query_store[query_id] = {
        "query_id": query_id,
        "status": "initiated",
        "query": query_request.query,
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
        "error": None,
        "answer": None,
        "sources": None,
        "processing_time": None
    }
    
    # Create and track the background task
    await task_manager.add_task(
        query_id,
        process_query_background(query_id, query_request.query, query_request.num_results)
    )
    
    return QueryResponse(**query_store[query_id])

@app.get("/query/{query_id}", response_model=QueryResponse)
async def get_query_result(query_id: str):
    logger.debug(f"Fetching results for query_id: {query_id}")
    if query_id not in query_store:
        logger.warning(f"Query ID not found: {query_id}")
        raise HTTPException(status_code=404, detail="Query not found")
    
    result = query_store[query_id]
    
    # Add task status information
    if query_id in task_manager.tasks:
        task = task_manager.tasks[query_id]
        if task.done():
            if task.exception():
                result["status"] = "failed"
                result["error"] = str(task.exception())
    
    logger.debug(f"Query status: {result['status']}")
    return QueryResponse(**result)

@app.get("/status")
async def get_system_status():
    return {
        "active_tasks": len(task_manager.tasks),
        "total_queries": len(query_store),
        "queries_by_status": {
            status: len([q for q in query_store.values() if q["status"] == status])
            for status in set(q["status"] for q in query_store.values())
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "api_keys_configured": bool(os.getenv("GROQ_API_KEY")) and bool(os.getenv("SERPER_API_KEY"))
    }

# Add middleware to log request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
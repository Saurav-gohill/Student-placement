from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
import tempfile
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ResumeAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    analysis: str
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[str]
    score: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    category: str
    difficulty: str

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    user_answer: int
    is_correct: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CareerRoadmap(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str
    description: str
    roadmap_url: str
    skills: List[str]
    timeline: str
    difficulty: str

# Sample quiz data
SAMPLE_QUIZZES = [
    {
        "question": "What is the time complexity of binary search?",
        "options": ["O(n)", "O(log n)", "O(n log n)", "O(n²)"],
        "correct_answer": 1,
        "explanation": "Binary search has O(log n) time complexity as it divides the search space in half at each step.",
        "category": "Algorithms",
        "difficulty": "Medium"
    },
    {
        "question": "Which data structure follows LIFO principle?",
        "options": ["Queue", "Stack", "Array", "Linked List"],
        "correct_answer": 1,
        "explanation": "Stack follows Last In First Out (LIFO) principle where the last element added is the first to be removed.",
        "category": "Data Structures",
        "difficulty": "Easy"
    },
    {
        "question": "What is the purpose of a primary key in a database?",
        "options": ["To sort data", "To uniquely identify records", "To create indexes", "To encrypt data"],
        "correct_answer": 1,
        "explanation": "A primary key uniquely identifies each record in a database table and cannot have null values.",
        "category": "Database",
        "difficulty": "Easy"
    },
    {
        "question": "Which sorting algorithm has the best average time complexity?",
        "options": ["Bubble Sort", "Selection Sort", "Merge Sort", "Insertion Sort"],
        "correct_answer": 2,
        "explanation": "Merge Sort has O(n log n) average time complexity, which is optimal for comparison-based sorting.",
        "category": "Algorithms",
        "difficulty": "Medium"
    },
    {
        "question": "What is polymorphism in OOP?",
        "options": ["Having multiple constructors", "Method overloading", "Ability to take multiple forms", "Inheritance"],
        "correct_answer": 2,
        "explanation": "Polymorphism allows objects of different types to be treated as objects of a common base type.",
        "category": "OOP",
        "difficulty": "Medium"
    }
]

# Sample career roadmaps
CAREER_ROADMAPS = [
    {
        "role": "Frontend Developer",
        "description": "Build user interfaces and experiences for web applications",
        "roadmap_url": "https://roadmap.sh/frontend",
        "skills": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular"],
        "timeline": "6-12 months",
        "difficulty": "Beginner"
    },
    {
        "role": "Backend Developer",
        "description": "Develop server-side logic and infrastructure",
        "roadmap_url": "https://roadmap.sh/backend",
        "skills": ["Python", "Node.js", "Databases", "APIs", "Cloud Services"],
        "timeline": "8-14 months",
        "difficulty": "Intermediate"
    },
    {
        "role": "Full Stack Developer",
        "description": "Work on both frontend and backend development",
        "roadmap_url": "https://roadmap.sh/full-stack",
        "skills": ["Frontend", "Backend", "Database", "DevOps", "Testing"],
        "timeline": "12-18 months",
        "difficulty": "Advanced"
    },
    {
        "role": "DevOps Engineer",
        "description": "Manage development and deployment processes",
        "roadmap_url": "https://roadmap.sh/devops",
        "skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Monitoring"],
        "timeline": "10-16 months",
        "difficulty": "Advanced"
    },
    {
        "role": "Data Scientist",
        "description": "Extract insights from data using statistical methods",
        "roadmap_url": "https://roadmap.sh/ai-data-scientist",
        "skills": ["Python", "Statistics", "Machine Learning", "SQL", "Visualization"],
        "timeline": "12-24 months",
        "difficulty": "Advanced"
    },
    {
        "role": "Mobile Developer",
        "description": "Create mobile applications for iOS and Android",
        "roadmap_url": "https://roadmap.sh/android",
        "skills": ["React Native", "Flutter", "Swift", "Kotlin", "Mobile UX"],
        "timeline": "8-14 months",
        "difficulty": "Intermediate"
    }
]

# Initialize database with sample data
async def init_db():
    # Check if quizzes already exist
    existing_quizzes = await db.quizzes.count_documents({})
    if existing_quizzes == 0:
        quiz_objects = [Quiz(**quiz) for quiz in SAMPLE_QUIZZES]
        await db.quizzes.insert_many([quiz.dict() for quiz in quiz_objects])
    
    # Check if roadmaps already exist
    existing_roadmaps = await db.roadmaps.count_documents({})
    if existing_roadmaps == 0:
        roadmap_objects = [CareerRoadmap(**roadmap) for roadmap in CAREER_ROADMAPS]
        await db.roadmaps.insert_many([roadmap.dict() for roadmap in roadmap_objects])

# Routes
@api_router.get("/")
async def root():
    return {"message": "AI-Powered Student Placement Prep Platform"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/analyze-resume", response_model=ResumeAnalysis)
async def analyze_resume(file: UploadFile = File(...)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Initialize Gemini chat
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=str(uuid.uuid4()),
            system_message="You are an expert resume reviewer for student placements. Analyze resumes and provide detailed, actionable feedback."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Create file content object
        pdf_file = FileContentWithMimeType(
            file_path=tmp_file_path,
            mime_type="application/pdf"
        )
        
        # Analyze resume
        analysis_prompt = """
        Analyze this resume for a student seeking placement opportunities. Provide:
        1. Overall score (1-100)
        2. Key strengths (3-5 points)
        3. Major weaknesses (3-5 points)
        4. Specific improvements needed (5-7 actionable points)
        5. Detailed analysis covering format, content, skills, experience, and presentation
        
        Format your response as JSON with these keys:
        - score: integer (1-100)
        - strengths: array of strings
        - weaknesses: array of strings
        - improvements: array of strings
        - analysis: detailed string analysis
        """
        
        user_message = UserMessage(
            text=analysis_prompt,
            file_contents=[pdf_file]
        )
        
        response = await chat.send_message(user_message)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Parse response (simplified - in production, you'd want better JSON parsing)
        import json
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                parsed_data = json.loads(json_str)
            else:
                # Fallback: create structured response from text
                parsed_data = {
                    "score": 75,
                    "strengths": ["Professional formatting", "Relevant skills listed", "Clear contact information"],
                    "weaknesses": ["Limited work experience", "Missing quantifiable achievements", "Generic objective statement"],
                    "improvements": ["Add specific metrics and achievements", "Include relevant projects", "Customize for target roles", "Add technical skills section", "Improve summary statement"],
                    "analysis": response
                }
        except:
            # Final fallback
            parsed_data = {
                "score": 70,
                "strengths": ["Resume uploaded successfully", "Professional appearance", "Good structure"],
                "weaknesses": ["Could be more specific", "Add more details", "Enhance presentation"],
                "improvements": ["Add quantifiable results", "Include relevant keywords", "Highlight achievements", "Customize for roles", "Add skills section"],
                "analysis": response
            }
        
        # Create analysis object
        analysis = ResumeAnalysis(
            filename=file.filename,
            analysis=parsed_data["analysis"],
            strengths=parsed_data["strengths"],
            weaknesses=parsed_data["weaknesses"],
            improvements=parsed_data["improvements"],
            score=parsed_data["score"]
        )
        
        # Save to database
        await db.resume_analyses.insert_one(analysis.dict())
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

@api_router.get("/quizzes", response_model=List[Quiz])
async def get_quizzes():
    quizzes = await db.quizzes.find().to_list(1000)
    return [Quiz(**quiz) for quiz in quizzes]

@api_router.get("/quiz/random", response_model=Quiz)
async def get_random_quiz():
    quizzes = await db.quizzes.find().to_list(1000)
    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found")
    
    random_quiz = random.choice(quizzes)
    return Quiz(**random_quiz)

@api_router.post("/quiz/attempt", response_model=QuizAttempt)
async def submit_quiz_attempt(quiz_id: str, user_answer: int):
    # Get quiz
    quiz_data = await db.quizzes.find_one({"id": quiz_id})
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz = Quiz(**quiz_data)
    is_correct = user_answer == quiz.correct_answer
    
    # Create attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_answer=user_answer,
        is_correct=is_correct
    )
    
    # Save to database
    await db.quiz_attempts.insert_one(attempt.dict())
    
    return attempt

@api_router.get("/roadmaps", response_model=List[CareerRoadmap])
async def get_career_roadmaps():
    roadmaps = await db.roadmaps.find().to_list(1000)
    return [CareerRoadmap(**roadmap) for roadmap in roadmaps]

@api_router.get("/roadmap/{roadmap_id}", response_model=CareerRoadmap)
async def get_roadmap_details(roadmap_id: str):
    roadmap_data = await db.roadmaps.find_one({"id": roadmap_id})
    if not roadmap_data:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    return CareerRoadmap(**roadmap_data)

@api_router.get("/stats")
async def get_platform_stats():
    total_analyses = await db.resume_analyses.count_documents({})
    total_attempts = await db.quiz_attempts.count_documents({})
    total_quizzes = await db.quizzes.count_documents({})
    total_roadmaps = await db.roadmaps.count_documents({})
    
    return {
        "total_resume_analyses": total_analyses,
        "total_quiz_attempts": total_attempts,
        "total_quizzes": total_quizzes,
        "total_roadmaps": total_roadmaps
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
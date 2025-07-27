#!/usr/bin/env python3
"""
Backend API Testing Script for AI-Powered Student Placement Prep Platform
Tests all backend endpoints according to test_result.md requirements
"""

import requests
import json
import os
import sys
from pathlib import Path
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time

# Load backend URL from frontend .env
def load_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return None

BACKEND_URL = load_backend_url()
if not BACKEND_URL:
    print("❌ ERROR: Could not load REACT_APP_BACKEND_URL from frontend/.env")
    sys.exit(1)

API_BASE_URL = f"{BACKEND_URL}/api"

print(f"🔗 Testing Backend API at: {API_BASE_URL}")
print("=" * 60)

def create_sample_pdf():
    """Create a sample PDF resume for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    # Create a simple PDF with resume content
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    
    # Add resume content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "John Smith")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "Software Engineer")
    c.drawString(100, height - 150, "Email: john.smith@email.com")
    c.drawString(100, height - 170, "Phone: (555) 123-4567")
    
    c.drawString(100, height - 210, "EXPERIENCE:")
    c.drawString(120, height - 230, "• Software Developer at Tech Corp (2022-2024)")
    c.drawString(120, height - 250, "• Developed web applications using React and Python")
    c.drawString(120, height - 270, "• Improved system performance by 30%")
    
    c.drawString(100, height - 310, "EDUCATION:")
    c.drawString(120, height - 330, "• Bachelor of Computer Science")
    c.drawString(120, height - 350, "• University of Technology (2018-2022)")
    c.drawString(120, height - 370, "• GPA: 3.8/4.0")
    
    c.drawString(100, height - 410, "SKILLS:")
    c.drawString(120, height - 430, "• Programming: Python, JavaScript, Java")
    c.drawString(120, height - 450, "• Frameworks: React, Django, Spring Boot")
    c.drawString(120, height - 470, "• Databases: MySQL, MongoDB")
    c.drawString(120, height - 490, "• Tools: Git, Docker, AWS")
    
    c.save()
    return temp_file.name

def test_basic_connectivity():
    """Test basic FastAPI server connectivity at /api/"""
    print("🔍 Testing Basic Server Connectivity...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server connectivity: SUCCESS")
            print(f"   Response: {data}")
            return True
        else:
            print(f"❌ Server connectivity: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connectivity: ERROR - {str(e)}")
        return False

def test_resume_analysis():
    """Test Gemini AI integration for resume analysis endpoint"""
    print("\n🔍 Testing Resume Analysis with PDF Upload...")
    
    # Create sample PDF
    pdf_path = create_sample_pdf()
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': ('sample_resume.pdf', pdf_file, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/analyze-resume", files=files, timeout=30)
        
        # Clean up temp file
        os.unlink(pdf_path)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ['id', 'filename', 'analysis', 'strengths', 'weaknesses', 'improvements', 'score']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"❌ Resume analysis: FAILED - Missing fields: {missing_fields}")
                return False
            
            print(f"✅ Resume analysis: SUCCESS")
            print(f"   Filename: {data['filename']}")
            print(f"   Score: {data['score']}/100")
            print(f"   Strengths: {len(data['strengths'])} items")
            print(f"   Weaknesses: {len(data['weaknesses'])} items")
            print(f"   Improvements: {len(data['improvements'])} items")
            print(f"   Analysis length: {len(data['analysis'])} characters")
            return True
        else:
            print(f"❌ Resume analysis: FAILED - Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        print(f"❌ Resume analysis: ERROR - {str(e)}")
        return False

def test_quiz_system():
    """Test quiz system endpoints: /api/quizzes, /api/quiz/random, /api/quiz/attempt"""
    print("\n🔍 Testing Quiz System...")
    
    # Test get all quizzes
    try:
        response = requests.get(f"{API_BASE_URL}/quizzes", timeout=10)
        if response.status_code != 200:
            print(f"❌ Get quizzes: FAILED - Status {response.status_code}")
            return False
        
        quizzes = response.json()
        if not quizzes or len(quizzes) == 0:
            print(f"❌ Get quizzes: FAILED - No quizzes returned")
            return False
        
        print(f"✅ Get quizzes: SUCCESS - {len(quizzes)} quizzes found")
        
        # Test get random quiz
        response = requests.get(f"{API_BASE_URL}/quiz/random", timeout=10)
        if response.status_code != 200:
            print(f"❌ Get random quiz: FAILED - Status {response.status_code}")
            return False
        
        random_quiz = response.json()
        required_fields = ['id', 'question', 'options', 'correct_answer', 'explanation', 'category', 'difficulty']
        missing_fields = [field for field in required_fields if field not in random_quiz]
        
        if missing_fields:
            print(f"❌ Get random quiz: FAILED - Missing fields: {missing_fields}")
            return False
        
        print(f"✅ Get random quiz: SUCCESS")
        print(f"   Question: {random_quiz['question'][:50]}...")
        print(f"   Category: {random_quiz['category']}")
        print(f"   Difficulty: {random_quiz['difficulty']}")
        
        # Test quiz attempt
        quiz_id = random_quiz['id']
        user_answer = 1  # Submit answer option 1
        
        response = requests.post(f"{API_BASE_URL}/quiz/attempt", 
                               params={'quiz_id': quiz_id, 'user_answer': user_answer}, 
                               timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Quiz attempt: FAILED - Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        attempt = response.json()
        required_fields = ['id', 'quiz_id', 'user_answer', 'is_correct', 'timestamp']
        missing_fields = [field for field in required_fields if field not in attempt]
        
        if missing_fields:
            print(f"❌ Quiz attempt: FAILED - Missing fields: {missing_fields}")
            return False
        
        print(f"✅ Quiz attempt: SUCCESS")
        print(f"   Quiz ID: {attempt['quiz_id']}")
        print(f"   User Answer: {attempt['user_answer']}")
        print(f"   Correct: {attempt['is_correct']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quiz system: ERROR - {str(e)}")
        return False

def test_career_roadmaps():
    """Test career roadmaps endpoints: /api/roadmaps, /api/roadmap/{id}"""
    print("\n🔍 Testing Career Roadmaps...")
    
    try:
        # Test get all roadmaps
        response = requests.get(f"{API_BASE_URL}/roadmaps", timeout=10)
        if response.status_code != 200:
            print(f"❌ Get roadmaps: FAILED - Status {response.status_code}")
            return False
        
        roadmaps = response.json()
        if not roadmaps or len(roadmaps) == 0:
            print(f"❌ Get roadmaps: FAILED - No roadmaps returned")
            return False
        
        print(f"✅ Get roadmaps: SUCCESS - {len(roadmaps)} roadmaps found")
        
        # Verify roadmap.sh URLs
        roadmap_sh_count = 0
        for roadmap in roadmaps:
            if 'roadmap_url' in roadmap and 'roadmap.sh' in roadmap['roadmap_url']:
                roadmap_sh_count += 1
        
        print(f"   Roadmap.sh URLs: {roadmap_sh_count}/{len(roadmaps)}")
        
        # Test get specific roadmap
        first_roadmap = roadmaps[0]
        roadmap_id = first_roadmap['id']
        
        response = requests.get(f"{API_BASE_URL}/roadmap/{roadmap_id}", timeout=10)
        if response.status_code != 200:
            print(f"❌ Get roadmap details: FAILED - Status {response.status_code}")
            return False
        
        roadmap_details = response.json()
        required_fields = ['id', 'role', 'description', 'roadmap_url', 'skills', 'timeline', 'difficulty']
        missing_fields = [field for field in required_fields if field not in roadmap_details]
        
        if missing_fields:
            print(f"❌ Get roadmap details: FAILED - Missing fields: {missing_fields}")
            return False
        
        print(f"✅ Get roadmap details: SUCCESS")
        print(f"   Role: {roadmap_details['role']}")
        print(f"   URL: {roadmap_details['roadmap_url']}")
        print(f"   Skills: {len(roadmap_details['skills'])} skills")
        print(f"   Timeline: {roadmap_details['timeline']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Career roadmaps: ERROR - {str(e)}")
        return False

def test_platform_statistics():
    """Test platform statistics endpoint /api/stats"""
    print("\n🔍 Testing Platform Statistics...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if response.status_code != 200:
            print(f"❌ Platform stats: FAILED - Status {response.status_code}")
            return False
        
        stats = response.json()
        required_fields = ['total_resume_analyses', 'total_quiz_attempts', 'total_quizzes', 'total_roadmaps']
        missing_fields = [field for field in required_fields if field not in stats]
        
        if missing_fields:
            print(f"❌ Platform stats: FAILED - Missing fields: {missing_fields}")
            return False
        
        print(f"✅ Platform statistics: SUCCESS")
        print(f"   Resume Analyses: {stats['total_resume_analyses']}")
        print(f"   Quiz Attempts: {stats['total_quiz_attempts']}")
        print(f"   Total Quizzes: {stats['total_quizzes']}")
        print(f"   Total Roadmaps: {stats['total_roadmaps']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Platform statistics: ERROR - {str(e)}")
        return False

def main():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base URL: {API_BASE_URL}")
    print("=" * 60)
    
    results = {}
    
    # Test basic connectivity first
    results['basic_connectivity'] = test_basic_connectivity()
    
    # Test all endpoints
    results['resume_analysis'] = test_resume_analysis()
    results['quiz_system'] = test_quiz_system()
    results['career_roadmaps'] = test_career_roadmaps()
    results['platform_statistics'] = test_platform_statistics()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend tests PASSED!")
        return True
    else:
        print("⚠️  Some backend tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
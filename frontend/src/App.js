import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState('resume');
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const Header = () => (
    <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-3xl font-bold text-center">🎓 AI-Powered Student Placement Prep</h1>
        <p className="text-center mt-2 text-blue-100">Your one-stop platform for placement preparation</p>
      </div>
    </header>
  );

  const Navigation = () => (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-center space-x-1">
          {[
            { id: 'resume', label: '📄 Resume Analysis', icon: '📄' },
            { id: 'quiz', label: '🧠 Daily Quiz', icon: '🧠' },
            { id: 'roadmap', label: '🗺️ Career Roadmaps', icon: '🗺️' },
            { id: 'mock', label: '🎭 Mock Interviews', icon: '🎭' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium rounded-lg transition-all duration-300 ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-blue-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );

  const ResumeAnalysis = () => {
    const [file, setFile] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [dragActive, setDragActive] = useState(false);

    const handleFileUpload = async (selectedFile) => {
      if (!selectedFile) return;
      
      setLoading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await axios.post(`${API}/analyze-resume`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setAnalysis(response.data);
      } catch (error) {
        console.error('Error analyzing resume:', error);
        alert('Error analyzing resume. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    const handleDrag = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === "dragenter" || e.type === "dragover") {
        setDragActive(true);
      } else if (e.type === "dragleave") {
        setDragActive(false);
      }
    };

    const handleDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const droppedFile = e.dataTransfer.files[0];
        setFile(droppedFile);
        handleFileUpload(droppedFile);
      }
    };

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">📄 AI Resume Analysis</h2>
          <p className="text-gray-600">Upload your resume and get detailed AI-powered feedback</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="text-4xl mb-4">📄</div>
            <p className="text-lg font-medium text-gray-700 mb-2">
              {file ? file.name : 'Drop your resume here or click to browse'}
            </p>
            <p className="text-gray-500 mb-4">Supports PDF files only</p>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => {
                const selectedFile = e.target.files[0];
                setFile(selectedFile);
                handleFileUpload(selectedFile);
              }}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
            >
              Choose File
            </label>
          </div>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Analyzing your resume with AI...</p>
          </div>
        )}

        {analysis && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="text-center mb-6">
              <div className="inline-block bg-blue-100 rounded-full p-4 mb-4">
                <span className="text-3xl font-bold text-blue-600">{analysis.score}/100</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-800">Analysis Results</h3>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-bold text-green-800 mb-3 flex items-center">
                  <span className="mr-2">✅</span> Strengths
                </h4>
                <ul className="space-y-2">
                  {analysis.strengths.map((strength, index) => (
                    <li key={index} className="text-green-700 text-sm">• {strength}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-red-50 rounded-lg p-4">
                <h4 className="font-bold text-red-800 mb-3 flex items-center">
                  <span className="mr-2">❌</span> Weaknesses
                </h4>
                <ul className="space-y-2">
                  {analysis.weaknesses.map((weakness, index) => (
                    <li key={index} className="text-red-700 text-sm">• {weakness}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-bold text-blue-800 mb-3 flex items-center">
                  <span className="mr-2">💡</span> Improvements
                </h4>
                <ul className="space-y-2">
                  {analysis.improvements.map((improvement, index) => (
                    <li key={index} className="text-blue-700 text-sm">• {improvement}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-bold text-gray-800 mb-3">📝 Detailed Analysis</h4>
              <p className="text-gray-700 whitespace-pre-line">{analysis.analysis}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const QuizSection = () => {
    const [currentQuiz, setCurrentQuiz] = useState(null);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [showResult, setShowResult] = useState(false);
    const [attempt, setAttempt] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchRandomQuiz = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API}/quiz/random`);
        setCurrentQuiz(response.data);
        setSelectedAnswer(null);
        setShowResult(false);
        setAttempt(null);
      } catch (error) {
        console.error('Error fetching quiz:', error);
      } finally {
        setLoading(false);
      }
    };

    const submitAnswer = async () => {
      if (selectedAnswer === null) return;
      
      try {
        const response = await axios.post(`${API}/quiz/attempt?quiz_id=${currentQuiz.id}&user_answer=${selectedAnswer}`);
        setAttempt(response.data);
        setShowResult(true);
      } catch (error) {
        console.error('Error submitting answer:', error);
      }
    };

    useEffect(() => {
      fetchRandomQuiz();
    }, []);

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">🧠 Daily Quiz Challenge</h2>
          <p className="text-gray-600">Test your knowledge with our curated questions</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-gray-600">Loading quiz...</p>
            </div>
          ) : currentQuiz ? (
            <div>
              <div className="flex justify-between items-center mb-6">
                <div className="flex space-x-4">
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                    {currentQuiz.category}
                  </span>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                    {currentQuiz.difficulty}
                  </span>
                </div>
                <button
                  onClick={fetchRandomQuiz}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  🎲 New Quiz
                </button>
              </div>

              <h3 className="text-xl font-bold text-gray-800 mb-6">{currentQuiz.question}</h3>

              <div className="space-y-3 mb-6">
                {currentQuiz.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => !showResult && setSelectedAnswer(index)}
                    disabled={showResult}
                    className={`w-full p-4 text-left rounded-lg border-2 transition-all duration-200 ${
                      showResult
                        ? index === currentQuiz.correct_answer
                          ? 'border-green-500 bg-green-50 text-green-800'
                          : index === selectedAnswer && selectedAnswer !== currentQuiz.correct_answer
                          ? 'border-red-500 bg-red-50 text-red-800'
                          : 'border-gray-200 bg-gray-50 text-gray-600'
                        : selectedAnswer === index
                        ? 'border-blue-500 bg-blue-50 text-blue-800'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50'
                    }`}
                  >
                    <span className="font-medium mr-3">{String.fromCharCode(65 + index)}.</span>
                    {option}
                  </button>
                ))}
              </div>

              {!showResult ? (
                <button
                  onClick={submitAnswer}
                  disabled={selectedAnswer === null}
                  className={`w-full py-3 rounded-lg font-medium transition-colors ${
                    selectedAnswer !== null
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Submit Answer
                </button>
              ) : (
                <div className="mt-6">
                  <div className={`p-4 rounded-lg ${attempt.is_correct ? 'bg-green-50' : 'bg-red-50'}`}>
                    <h4 className={`font-bold mb-2 ${attempt.is_correct ? 'text-green-800' : 'text-red-800'}`}>
                      {attempt.is_correct ? '✅ Correct!' : '❌ Incorrect'}
                    </h4>
                    <p className="text-gray-700">{currentQuiz.explanation}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-center text-gray-500">No quiz available</p>
          )}
        </div>
      </div>
    );
  };

  const CareerRoadmaps = () => {
    const [roadmaps, setRoadmaps] = useState([]);
    const [selectedRoadmap, setSelectedRoadmap] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      fetchRoadmaps();
    }, []);

    const fetchRoadmaps = async () => {
      try {
        const response = await axios.get(`${API}/roadmaps`);
        setRoadmaps(response.data);
      } catch (error) {
        console.error('Error fetching roadmaps:', error);
      } finally {
        setLoading(false);
      }
    };

    const openRoadmap = (roadmap) => {
      setSelectedRoadmap(roadmap);
      window.open(roadmap.roadmap_url, '_blank');
    };

    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">🗺️ Career Roadmaps</h2>
          <p className="text-gray-600">Choose your path and follow structured learning roadmaps</p>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading roadmaps...</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {roadmaps.map((roadmap) => (
              <div
                key={roadmap.id}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-2">{roadmap.role}</h3>
                <p className="text-gray-600 mb-4">{roadmap.description}</p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {roadmap.skills.slice(0, 3).map((skill, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                  {roadmap.skills.length > 3 && (
                    <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm">
                      +{roadmap.skills.length - 3} more
                    </span>
                  )}
                </div>

                <div className="flex justify-between items-center mb-4">
                  <span className="text-sm text-gray-500">⏱️ {roadmap.timeline}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    roadmap.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                    roadmap.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {roadmap.difficulty}
                  </span>
                </div>

                <button
                  onClick={() => openRoadmap(roadmap)}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  View Roadmap →
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const MockInterviews = () => {
    const [mockInterviews, setMockInterviews] = useState([]);
    const [selectedInterview, setSelectedInterview] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [responses, setResponses] = useState([]);
    const [currentResponse, setCurrentResponse] = useState('');
    const [practiceResult, setPracticeResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState('select'); // 'select', 'practice', 'result'

    useEffect(() => {
      fetchMockInterviews();
    }, []);

    const fetchMockInterviews = async () => {
      try {
        const response = await axios.get(`${API}/mock-interviews`);
        setMockInterviews(response.data);
      } catch (error) {
        console.error('Error fetching mock interviews:', error);
      }
    };

    const startInterview = (interview) => {
      setSelectedInterview(interview);
      setCurrentQuestion(0);
      setResponses([]);
      setCurrentResponse('');
      setPracticeResult(null);
      setMode('practice');
    };

    const saveResponse = () => {
      if (currentResponse.trim()) {
        const newResponses = [...responses, currentResponse];
        setResponses(newResponses);
        setCurrentResponse('');
        
        if (currentQuestion < selectedInterview.questions.length - 1) {
          setCurrentQuestion(currentQuestion + 1);
        } else {
          submitInterview(newResponses);
        }
      }
    };

    const submitInterview = async (finalResponses) => {
      setLoading(true);
      try {
        const response = await axios.post(`${API}/mock-interview/practice`, null, {
          params: {
            interview_id: selectedInterview.id,
            user_responses: finalResponses
          }
        });
        setPracticeResult(response.data);
        setMode('result');
      } catch (error) {
        console.error('Error submitting interview:', error);
        alert('Error submitting interview. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    const resetInterview = () => {
      setMode('select');
      setSelectedInterview(null);
      setCurrentQuestion(0);
      setResponses([]);
      setCurrentResponse('');
      setPracticeResult(null);
    };

    if (mode === 'select') {
      return (
        <div className="max-w-6xl mx-auto p-6">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-2">🎭 Mock Interviews</h2>
            <p className="text-gray-600">Practice with role-specific interview questions</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockInterviews.map((interview) => (
              <div
                key={interview.id}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-3">{interview.role}</h3>
                <p className="text-gray-600 mb-4">{interview.questions.length} practice questions</p>
                
                <div className="flex justify-between items-center mb-4">
                  <span className="text-sm text-gray-500">⏱️ {interview.duration}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    interview.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                    interview.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {interview.difficulty}
                  </span>
                </div>

                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">💡 Interview Tips:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {interview.tips.slice(0, 2).map((tip, index) => (
                      <li key={index}>• {tip}</li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => startInterview(interview)}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  Start Practice →
                </button>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (mode === 'practice') {
      return (
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">{selectedInterview.role} Interview</h2>
              <button
                onClick={resetInterview}
                className="text-gray-500 hover:text-gray-700 font-medium"
              >
                ← Back to Selection
              </button>
            </div>

            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-500">
                  Question {currentQuestion + 1} of {selectedInterview.questions.length}
                </span>
                <span className="text-sm text-gray-500">
                  {Math.round(((currentQuestion + 1) / selectedInterview.questions.length) * 100)}% Complete
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentQuestion + 1) / selectedInterview.questions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {selectedInterview.questions[currentQuestion]}
              </h3>
              
              <textarea
                value={currentResponse}
                onChange={(e) => setCurrentResponse(e.target.value)}
                placeholder="Type your response here..."
                className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex justify-between">
              <button
                onClick={resetInterview}
                className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={saveResponse}
                disabled={!currentResponse.trim()}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  currentResponse.trim()
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {currentQuestion < selectedInterview.questions.length - 1 ? 'Next Question' : 'Submit Interview'}
              </button>
            </div>
          </div>
        </div>
      );
    }

    if (mode === 'result') {
      return (
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Interview Complete!</h2>
              <p className="text-gray-600">Here's your performance summary</p>
            </div>

            <div className="text-center mb-8">
              <div className="inline-block bg-blue-100 rounded-full p-6 mb-4">
                <span className="text-4xl font-bold text-blue-600">{practiceResult.score}/100</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800">Interview Score</h3>
            </div>

            <div className="bg-gray-50 rounded-lg p-6 mb-6">
              <h4 className="font-bold text-gray-800 mb-3">📝 Feedback</h4>
              <p className="text-gray-700">{practiceResult.feedback}</p>
            </div>

            <div className="bg-blue-50 rounded-lg p-6 mb-6">
              <h4 className="font-bold text-blue-800 mb-3">💡 Interview Tips for {selectedInterview.role}</h4>
              <ul className="space-y-2">
                {selectedInterview.tips.map((tip, index) => (
                  <li key={index} className="text-blue-700 text-sm">• {tip}</li>
                ))}
              </ul>
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={() => startInterview(selectedInterview)}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Practice Again
              </button>
              <button
                onClick={resetInterview}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                Try Different Role
              </button>
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'resume':
        return <ResumeAnalysis />;
      case 'quiz':
        return <QuizSection />;
      case 'roadmap':
        return <CareerRoadmaps />;
      case 'mock':
        return <MockInterviews />;
      default:
        return <ResumeAnalysis />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Navigation />
      
      <main className="container mx-auto py-8">
        {renderContent()}
      </main>

      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <div className="grid md:grid-cols-4 gap-6 mb-6">
            <div>
              <h4 className="font-bold mb-2">📊 Platform Stats</h4>
              <p className="text-sm text-gray-300">Resume Analyses: {stats.total_resume_analyses || 0}</p>
              <p className="text-sm text-gray-300">Quiz Attempts: {stats.total_quiz_attempts || 0}</p>
            </div>
            <div>
              <h4 className="font-bold mb-2">🎯 Features</h4>
              <p className="text-sm text-gray-300">AI Resume Feedback</p>
              <p className="text-sm text-gray-300">Daily Quizzes</p>
            </div>
            <div>
              <h4 className="font-bold mb-2">🗺️ Roadmaps</h4>
              <p className="text-sm text-gray-300">Career Paths: {stats.total_roadmaps || 0}</p>
              <p className="text-sm text-gray-300">Skill Development</p>
            </div>
            <div>
              <h4 className="font-bold mb-2">🎭 Mock Interviews</h4>
              <p className="text-sm text-gray-300">Interview Practices: {stats.total_interview_practices || 0}</p>
              <p className="text-sm text-gray-300">Available Roles: {stats.total_mock_interviews || 0}</p>
            </div>
          </div>
          <p className="text-gray-400">© 2025 AI-Powered Student Placement Prep Platform</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
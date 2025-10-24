"""
Test configuration and utilities.

Provides pytest configuration, fixtures, and shared test utilities.
"""

import pytest
import os
import sys
from unittest.mock import Mock

# Add src directory to Python path for importing modules
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(TEST_DIR, '..', 'src')
sys.path.insert(0, SRC_DIR)


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    EXPERIENCE:
    Senior Software Engineer - Tech Corp (2020-Present)
    • Developed web applications using Python and JavaScript
    • Led team of 5 developers on cloud migration project
    • Improved system performance by 40% through optimization
    • Implemented CI/CD pipelines reducing deployment time by 60%
    
    Software Engineer - StartupXYZ (2018-2020)
    • Built REST APIs using Django and PostgreSQL
    • Collaborated with cross-functional teams on product features
    • Maintained code coverage above 90% through comprehensive testing
    
    EDUCATION:
    Bachelor of Science in Computer Science
    University of Technology (2014-2018)
    GPA: 3.8/4.0
    
    SKILLS:
    Programming: Python, JavaScript, Java, SQL
    Frameworks: Django, React, Node.js
    Tools: Git, Docker, AWS, Jenkins
    Databases: PostgreSQL, MongoDB, Redis
    
    PROJECTS:
    E-commerce Platform - Built scalable platform handling 10k+ daily users
    ML Recommendation System - Developed recommendation engine increasing sales by 25%
    """


@pytest.fixture
def sample_skills():
    """Sample skills list for testing."""
    return [
        "Python",
        "JavaScript", 
        "Machine Learning",
        "SQL",
        "Git",
        "AWS",
        "Django",
        "React",
        "Docker",
        "Data Analysis"
    ]


@pytest.fixture
def sample_job_preferences():
    """Sample job preferences for testing."""
    return {
        "location": "Remote",
        "salary_range": "$80k-120k",
        "industry": "Technology",
        "remote_ok": True,
        "company_size": "Startup to Mid-size",
        "role_level": "Senior"
    }


@pytest.fixture
def sample_interview_questions():
    """Sample interview questions for testing."""
    return [
        "Tell me about yourself and your background in software engineering.",
        "What experience do you have with Python and web development?",
        "Describe a challenging technical problem you've solved recently.",
        "How do you approach debugging complex issues in production?",
        "What interests you most about this role and our company?",
        "How do you stay updated with new technologies and best practices?",
        "Describe a time when you had to work with a difficult team member.",
        "What's your experience with cloud technologies like AWS?"
    ]


@pytest.fixture
def sample_interview_answers():
    """Sample interview answers for testing."""
    return [
        "I'm a software engineer with 5 years of experience in full-stack development. I specialize in Python and JavaScript, and have led several successful projects.",
        "I have extensive experience with Python, particularly with Django for web development. I've built several REST APIs and worked with databases like PostgreSQL.",
        "Recently, I had to optimize a slow database query that was affecting our API performance. I analyzed the query execution plan and added proper indexes, reducing response time by 70%.",
        "My debugging approach is systematic. I start by reproducing the issue, then use logging and monitoring tools to identify the root cause. I also write tests to prevent regression.",
        "I'm excited about this role because it combines my technical skills with leadership opportunities. Your company's focus on innovation and growth aligns with my career goals.",
        "I regularly read tech blogs, participate in online communities, attend conferences, and work on side projects to experiment with new technologies.",
        "I once worked with a colleague who was resistant to code reviews. I approached them privately, explained the benefits, and offered to pair program to make the process more collaborative.",
        "I have hands-on experience with AWS services including EC2, S3, RDS, and Lambda. I've deployed applications using Docker containers and managed infrastructure as code."
    ]


class MockConfig:
    """Mock configuration class for testing."""
    
    def __init__(self):
        self.discord_bot_token = "mock_discord_token"
        self.llm_provider = "openai"
        self.openai_api_key = "mock_openai_key"
        self.anthropic_api_key = None
        self.log_level = "INFO"
        self.log_dir = "logs"
        self.max_resume_length = 10000
        self.max_interview_questions = 10
        self.default_timeout = 30
    
    def is_development(self):
        return True
    
    def get_log_file_path(self, component):
        return f"logs/{component}.log"


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    return MockConfig()


def create_mock_llm_response(content):
    """Create a mock LLM response object."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = content
    return mock_response


def create_mock_discord_context():
    """Create a mock Discord context for testing."""
    ctx = Mock()
    ctx.send = Mock()
    ctx.author = Mock()
    ctx.author.id = 12345
    ctx.message = Mock()
    ctx.message.attachments = []
    ctx.typing = Mock()
    return ctx


# Test data constants
VALID_SKILLS = [
    "Python", "JavaScript", "Java", "C++", "SQL", "HTML", "CSS",
    "React", "Vue.js", "Angular", "Django", "Flask", "Node.js",
    "Git", "Docker", "AWS", "Azure", "Kubernetes", "Jenkins",
    "Machine Learning", "Data Science", "AI", "Statistics"
]

INVALID_SKILLS = [
    "", "   ", None, "A" * 200  # Empty, whitespace, None, too long
]

SAMPLE_CAREER_RECOMMENDATIONS = [
    {
        "job_title": "Senior Python Developer",
        "match_percentage": 92,
        "required_skills": ["Python", "Django", "SQL", "Git"],
        "skill_gaps": ["Kubernetes", "Microservices"],
        "salary_range": "$90k-130k",
        "career_path": ["Python Developer", "Senior Python Developer", "Tech Lead"],
        "reasoning": "Excellent match based on strong Python skills and web development experience"
    },
    {
        "job_title": "Full Stack Engineer", 
        "match_percentage": 88,
        "required_skills": ["JavaScript", "Python", "React", "SQL"],
        "skill_gaps": ["GraphQL", "TypeScript"],
        "salary_range": "$85k-120k",
        "career_path": ["Full Stack Developer", "Senior Full Stack Engineer", "Engineering Manager"],
        "reasoning": "Great fit with both frontend and backend experience"
    },
    {
        "job_title": "Data Scientist",
        "match_percentage": 75,
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL"],
        "skill_gaps": ["Deep Learning", "R", "Advanced Statistics"],
        "salary_range": "$95k-140k",
        "career_path": ["Data Analyst", "Data Scientist", "Senior Data Scientist"],
        "reasoning": "Good foundation with Python and ML, but needs more statistical background"
    }
]

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names."""
    for item in items:
        # Mark slow tests
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests (default for most tests)
        if not any(marker.name in ["slow", "integration"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
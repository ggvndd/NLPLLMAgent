"""
Unit tests for the Career Agent core functionality.

Tests career path analysis, resume review, job matching, skill gap analysis,
and mock interview features.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from career_agent import (
    CareerAgent, UserProfile, CareerRecommendation, 
    ResumeAnalysis, InterviewFeedback, AnalysisType
)
from config import Config
from utils.validators import InputValidator, ValidationResult


class TestCareerAgent:
    """Test cases for the CareerAgent class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=Config)
        config.llm_provider = "openai"
        config.openai_api_key = "test_key"
        config.anthropic_api_key = None
        config.log_level = "INFO"
        return config
    
    @pytest.fixture
    def sample_user_profile(self):
        """Create a sample user profile for testing."""
        return UserProfile(
            skills=["Python", "Machine Learning", "SQL"],
            experience=["2 years software development"],
            interests=["AI", "Data Science"],
            education=["Bachelor's Computer Science"],
            career_goals="Become a data scientist"
        )
    
    @pytest.fixture
    def career_agent(self, mock_config):
        """Create a CareerAgent instance with mocked LLM client."""
        with patch('career_agent.CareerAgent._initialize_llm_client') as mock_init:
            mock_llm = AsyncMock()
            mock_init.return_value = mock_llm
            
            agent = CareerAgent(mock_config)
            agent.llm_client = mock_llm
            return agent
    
    @pytest.mark.asyncio
    async def test_career_path_analysis_success(self, career_agent, sample_user_profile):
        """Test successful career path analysis."""
        # Mock LLM response
        mock_response = '''[
            {
                "job_title": "Data Scientist",
                "match_percentage": 85,
                "required_skills": ["Python", "Machine Learning", "Statistics"],
                "skill_gaps": ["Statistics", "Deep Learning"],
                "salary_range": "$90k-130k",
                "career_path": ["Junior Data Scientist", "Data Scientist", "Senior Data Scientist"],
                "reasoning": "Strong match based on Python and ML skills"
            }
        ]'''
        
        career_agent.llm_client.ChatCompletion.acreate.return_value.choices = [
            Mock(message=Mock(content=mock_response))
        ]
        
        # Test the analysis
        recommendations = await career_agent.analyze_career_path(sample_user_profile)
        
        # Assertions
        assert len(recommendations) == 1
        assert recommendations[0].job_title == "Data Scientist"
        assert recommendations[0].match_percentage == 85
        assert "Statistics" in recommendations[0].skill_gaps
    
    @pytest.mark.asyncio
    async def test_resume_review_success(self, career_agent):
        """Test successful resume review."""
        resume_text = """
        John Doe
        Software Engineer
        
        Experience:
        - 3 years Python development
        - Machine Learning projects
        
        Education:
        - Bachelor's Computer Science
        
        Skills:
        - Python, SQL, Git
        """
        
        # Mock LLM response
        mock_response = '''{
            "overall_score": 78,
            "strengths": ["Clear technical skills", "Relevant experience"],
            "weaknesses": ["Missing metrics", "No leadership examples"],
            "improvement_suggestions": ["Add quantifiable achievements", "Include soft skills"],
            "keyword_optimization": ["Add cloud technologies", "Include frameworks"],
            "formatting_feedback": ["Use consistent formatting", "Add contact info"]
        }'''
        
        career_agent.llm_client.ChatCompletion.acreate.return_value.choices = [
            Mock(message=Mock(content=mock_response))
        ]
        
        # Test the review
        analysis = await career_agent.review_resume(resume_text)
        
        # Assertions
        assert analysis.overall_score == 78
        assert len(analysis.strengths) == 2
        assert "Add quantifiable achievements" in analysis.improvement_suggestions
    
    @pytest.mark.asyncio
    async def test_job_matching_success(self, career_agent, sample_user_profile):
        """Test successful job matching."""
        job_preferences = {
            "location": "Remote",
            "salary_range": "$80k+",
            "industry": "Tech"
        }
        
        # Mock LLM response
        mock_response = '''[
            {
                "job_title": "Senior Python Developer",
                "company_type": "Tech Startup",
                "match_percentage": 92,
                "salary_range": "$85k-110k",
                "location": "Remote",
                "requirements": ["Python", "APIs", "Testing"]
            }
        ]'''
        
        career_agent.llm_client.ChatCompletion.acreate.return_value.choices = [
            Mock(message=Mock(content=mock_response))
        ]
        
        # Test job matching
        matches = await career_agent.match_jobs(sample_user_profile, job_preferences)
        
        # Assertions
        assert len(matches) == 1
        assert matches[0]["job_title"] == "Senior Python Developer"
        assert matches[0]["match_percentage"] == 92
    
    @pytest.mark.asyncio
    async def test_mock_interview_creation(self, career_agent):
        """Test mock interview session creation."""
        role = "Software Engineer"
        
        # Mock LLM response for question generation
        mock_response = '''[
            "Tell me about yourself",
            "What's your experience with Python?",
            "How do you handle debugging complex issues?",
            "Describe a challenging project you worked on"
        ]'''
        
        career_agent.llm_client.ChatCompletion.acreate.return_value.choices = [
            Mock(message=Mock(content=mock_response))
        ]
        
        # Test interview creation
        session = await career_agent.conduct_mock_interview(role)
        
        # Assertions
        assert session["role"] == role
        assert "questions" in session
        assert "session_id" in session
        assert "start_time" in session
    
    @pytest.mark.asyncio
    async def test_interview_evaluation(self, career_agent):
        """Test interview answer evaluation."""
        session_id = "test_session"
        answers = [
            "I'm a software engineer with 3 years of experience in Python development",
            "I have extensive experience with Python, including web development and data analysis",
            "I approach debugging systematically by reproducing the issue and using debugging tools"
        ]
        
        # Mock LLM response
        mock_response = '''{
            "overall_performance": 82,
            "communication_skills": 85,
            "technical_knowledge": 80,
            "problem_solving": 78,
            "areas_for_improvement": ["Provide more specific examples", "Show leadership experience"],
            "suggested_practice_topics": ["System design", "Behavioral questions"]
        }'''
        
        career_agent.llm_client.ChatCompletion.acreate.return_value.choices = [
            Mock(message=Mock(content=mock_response))
        ]
        
        # Test evaluation
        feedback = await career_agent.evaluate_interview_answers(session_id, answers)
        
        # Assertions
        assert feedback.overall_performance == 82
        assert feedback.communication_skills == 85
        assert len(feedback.areas_for_improvement) == 2
    
    @pytest.mark.asyncio
    async def test_skill_gap_analysis(self, career_agent):
        """Test skill gap analysis functionality."""
        current_skills = ["Python", "SQL"]
        target_role = "Data Scientist"
        
        # Mock LLM response
        mock_response = '''{
            "relevant_skills": ["Python", "SQL"],
            "missing_skills": ["Machine Learning", "Statistics", "R"],
            "learning_path": ["Learn Statistics fundamentals", "Master scikit-learn", "Practice with real datasets"],
            "timeline": "4-6 months",
            "resources": ["Coursera ML Course", "Kaggle competitions", "Statistics textbooks"]
        }'''
        
        career_agent.llm_client.ChatCompletion.acreate.return_value.choices = [
            Mock(message=Mock(content=mock_response))
        ]
        
        # Test skill gap analysis
        analysis = await career_agent.analyze_skill_gap(current_skills, target_role)
        
        # Assertions
        assert "Python" in analysis["relevant_skills"]
        assert "Machine Learning" in analysis["missing_skills"]
        assert analysis["timeline"] == "4-6 months"
    
    def test_fallback_recommendations(self, career_agent, sample_user_profile):
        """Test fallback recommendations when LLM parsing fails."""
        # Test the fallback method directly
        recommendations = career_agent._create_fallback_recommendations(sample_user_profile)
        
        # Assertions
        assert len(recommendations) > 0
        assert all(isinstance(rec, CareerRecommendation) for rec in recommendations)
        assert all(rec.match_percentage > 0 for rec in recommendations)


class TestInputValidator:
    """Test cases for input validation utilities."""
    
    def test_validate_skills_list_valid(self):
        """Test validation of valid skills list."""
        skills = ["Python", "Machine Learning", "SQL", "Git"]
        result = InputValidator.validate_skills_list(skills)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_skills_list_empty(self):
        """Test validation of empty skills list."""
        skills = []
        result = InputValidator.validate_skills_list(skills)
        
        assert not result.is_valid
        assert "Skills list cannot be empty" in result.errors
    
    def test_validate_skills_list_with_duplicates(self):
        """Test validation of skills list with duplicates."""
        skills = ["Python", "python", "SQL"]
        result = InputValidator.validate_skills_list(skills)
        
        assert result.is_valid  # Should still be valid
        assert "Duplicate skills found" in result.warnings
    
    def test_validate_resume_text_valid(self):
        """Test validation of valid resume text."""
        resume_text = """
        John Doe
        Software Engineer
        
        Experience:
        - 3 years Python development
        - Led team of 5 developers
        
        Education:
        - Bachelor's Computer Science
        
        Skills:
        - Python, JavaScript, SQL
        
        Contact: john@email.com, (555) 123-4567
        """
        
        result = InputValidator.validate_resume_text(resume_text)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_resume_text_empty(self):
        """Test validation of empty resume text."""
        resume_text = ""
        result = InputValidator.validate_resume_text(resume_text)
        
        assert not result.is_valid
        assert "Resume text cannot be empty" in result.errors
    
    def test_validate_resume_text_too_long(self):
        """Test validation of overly long resume text."""
        resume_text = "A" * 15000  # Exceeds default limit
        result = InputValidator.validate_resume_text(resume_text, max_length=10000)
        
        assert not result.is_valid
        assert "Resume text too long" in result.errors[0]
    
    def test_validate_job_preferences_valid(self):
        """Test validation of valid job preferences."""
        preferences = {
            "location": "Remote",
            "salary_range": "$80k-100k",
            "industry": "Technology",
            "remote_ok": True
        }
        
        result = InputValidator.validate_job_preferences(preferences)
        
        assert result.is_valid
    
    def test_validate_job_preferences_empty(self):
        """Test validation of empty job preferences."""
        preferences = {}
        result = InputValidator.validate_job_preferences(preferences)
        
        assert not result.is_valid
        assert "Job preferences cannot be empty" in result.errors
    
    def test_validate_interview_answers_valid(self):
        """Test validation of valid interview answers."""
        answers = [
            "I have 3 years of experience in software development",
            "My strengths include problem-solving and teamwork",
            "I'm interested in this role because of the growth opportunities"
        ]
        
        result = InputValidator.validate_interview_answers(answers)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_interview_answers_empty(self):
        """Test validation of empty interview answers."""
        answers = []
        result = InputValidator.validate_interview_answers(answers)
        
        assert not result.is_valid
        assert "No interview answers provided" in result.errors
    
    def test_validate_target_role_valid(self):
        """Test validation of valid target role."""
        role = "Senior Software Engineer"
        result = InputValidator.validate_target_role(role)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_target_role_empty(self):
        """Test validation of empty target role."""
        role = ""
        result = InputValidator.validate_target_role(role)
        
        assert not result.is_valid
        assert "Target role cannot be empty" in result.errors
    
    def test_sanitize_user_input(self):
        """Test user input sanitization."""
        dirty_input = "  Hello <script>alert('xss')</script> World!  \n\n  "
        clean_input = InputValidator.sanitize_user_input(dirty_input)
        
        assert "<script>" not in clean_input
        assert clean_input.strip() == "Hello alert('xss') World!"
    
    def test_extract_skills_from_text(self):
        """Test skill extraction from text."""
        text = "I have experience with Python, JavaScript, and AWS. I also know Docker and Git."
        skills = InputValidator.extract_skills_from_text(text)
        
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "AWS" in skills


class TestConfig:
    """Test cases for configuration management."""
    
    def test_config_validation_missing_discord_token(self):
        """Test configuration validation with missing Discord token."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config()
            assert "DISCORD_BOT_TOKEN is required" in str(exc_info.value)
    
    def test_config_validation_missing_llm_key(self):
        """Test configuration validation with missing LLM API key."""
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "LLM_PROVIDER": "openai"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config()
            assert "OPENAI_API_KEY is required" in str(exc_info.value)
    
    def test_config_valid_configuration(self):
        """Test valid configuration setup."""
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_discord_token",
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "test_openai_key",
            "LOG_LEVEL": "DEBUG"
        }, clear=True):
            config = Config()
            
            assert config.discord_bot_token == "test_discord_token"
            assert config.llm_provider == "openai"
            assert config.openai_api_key == "test_openai_key"
            assert config.log_level == "DEBUG"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
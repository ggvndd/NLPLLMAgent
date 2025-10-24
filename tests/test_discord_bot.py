"""
Unit tests for Discord bot functionality.

Tests Discord command handling, user interactions, and bot responses.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from discord_bot import create_bot
from career_agent import UserProfile
from config import Config


class TestDiscordBot:
    """Test cases for Discord bot commands and functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=Config)
        config.discord_bot_token = "test_token"
        config.llm_provider = "openai"
        config.openai_api_key = "test_key"
        config.log_level = "INFO"
        return config
    
    @pytest.fixture
    def mock_ctx(self):
        """Create a mock Discord context for testing."""
        ctx = Mock()
        ctx.send = AsyncMock()
        ctx.author = Mock()
        ctx.author.id = 12345
        ctx.message = Mock()
        ctx.message.attachments = []
        ctx.typing = Mock()
        ctx.typing.return_value.__aenter__ = AsyncMock()
        ctx.typing.return_value.__aexit__ = AsyncMock()
        return ctx
    
    @pytest.fixture
    def mock_bot(self, mock_config):
        """Create a mock Discord bot for testing."""
        with patch('discord_bot.CareerAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent_class.return_value = mock_agent
            
            bot = create_bot(mock_config)
            bot.career_agent = mock_agent
            return bot
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_bot, mock_ctx):
        """Test the help command functionality."""
        # Get the help command
        help_cmd = mock_bot.get_command('help')
        
        # Execute the command
        await help_cmd.callback(mock_ctx)
        
        # Verify help message was sent
        mock_ctx.send.assert_called_once()
        call_args = mock_ctx.send.call_args
        
        # Check that an embed was sent
        assert 'embed' in call_args.kwargs or len(call_args.args) > 0
    
    @pytest.mark.asyncio
    async def test_career_analyze_command_valid_input(self, mock_bot, mock_ctx):
        """Test career analysis command with valid input."""
        # Mock career agent response
        from career_agent import CareerRecommendation
        mock_recommendations = [
            CareerRecommendation(
                job_title="Data Scientist",
                match_percentage=85.0,
                required_skills=["Python", "Machine Learning"],
                skill_gaps=["Statistics"],
                salary_range="$90k-130k",
                career_path=["Junior", "Senior"],
                reasoning="Good match"
            )
        ]
        
        mock_bot.career_agent.analyze_career_path.return_value = mock_recommendations
        
        # Get and execute command
        cmd = mock_bot.get_command('career_analyze')
        await cmd.callback(mock_ctx, skills_input="Python, Machine Learning, SQL")
        
        # Verify agent was called and response was sent
        mock_bot.career_agent.analyze_career_path.assert_called_once()
        mock_ctx.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_career_analyze_command_invalid_input(self, mock_bot, mock_ctx):
        """Test career analysis command with invalid input."""
        cmd = mock_bot.get_command('career_analyze')
        
        # Test with empty skills
        await cmd.callback(mock_ctx, skills_input="")
        
        # Should send error message
        mock_ctx.send.assert_called_once()
        call_args = mock_ctx.send.call_args[0][0]
        assert "validation failed" in call_args.lower() or "❌" in call_args
    
    @pytest.mark.asyncio
    async def test_resume_review_no_attachment(self, mock_bot, mock_ctx):
        """Test resume review command without attachment."""
        # Mock no attachments
        mock_ctx.message.attachments = []
        
        cmd = mock_bot.get_command('resume_review')
        await cmd.callback(mock_ctx)
        
        # Should request file attachment
        mock_ctx.send.assert_called_once()
        call_args = mock_ctx.send.call_args[0][0]
        assert "attach" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_resume_review_with_valid_attachment(self, mock_bot, mock_ctx):
        """Test resume review command with valid attachment."""
        # Mock attachment
        mock_attachment = Mock()
        mock_attachment.filename = "resume.txt"
        mock_attachment.size = 1000
        mock_attachment.read = AsyncMock(return_value=b"Sample resume content")
        mock_ctx.message.attachments = [mock_attachment]
        
        # Mock career agent response
        from career_agent import ResumeAnalysis
        mock_analysis = ResumeAnalysis(
            overall_score=78.0,
            strengths=["Clear format"],
            weaknesses=["Missing metrics"],
            improvement_suggestions=["Add achievements"],
            keyword_optimization=["Add keywords"],
            formatting_feedback=["Improve layout"]
        )
        mock_bot.career_agent.review_resume.return_value = mock_analysis
        
        cmd = mock_bot.get_command('resume_review')
        await cmd.callback(mock_ctx)
        
        # Verify resume was analyzed
        mock_bot.career_agent.review_resume.assert_called_once()
        mock_ctx.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_job_match_command(self, mock_bot, mock_ctx):
        """Test job matching command."""
        # Mock career agent response
        mock_matches = [
            {
                "job_title": "Software Engineer",
                "match_percentage": 90,
                "company_type": "Tech Startup",
                "salary_range": "$80k-120k",
                "location": "Remote"
            }
        ]
        mock_bot.career_agent.match_jobs.return_value = mock_matches
        
        cmd = mock_bot.get_command('job_match')
        await cmd.callback(mock_ctx, preferences="Remote, Tech, $80k+")
        
        # Verify job matching was called
        mock_bot.career_agent.match_jobs.assert_called_once()
        mock_ctx.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mock_interview_command(self, mock_bot, mock_ctx):
        """Test mock interview command."""
        # Mock career agent response
        mock_session = {
            "role": "Software Engineer",
            "questions": [
                "Tell me about yourself",
                "What's your experience with Python?"
            ],
            "session_id": "test_session",
            "start_time": "2024-01-01T00:00:00"
        }
        mock_bot.career_agent.conduct_mock_interview.return_value = mock_session
        
        cmd = mock_bot.get_command('mock_interview')
        await cmd.callback(mock_ctx, role="Software Engineer")
        
        # Verify interview session was created
        mock_bot.career_agent.conduct_mock_interview.assert_called_once_with("Software Engineer")
        mock_ctx.send.assert_called_once()
        
        # Verify session was stored
        assert mock_ctx.author.id in mock_bot.interview_sessions
    
    @pytest.mark.asyncio
    async def test_skill_gap_command_valid_format(self, mock_bot, mock_ctx):
        """Test skill gap analysis command with valid format."""
        # Mock career agent response
        mock_analysis = {
            "relevant_skills": ["Python"],
            "missing_skills": ["Machine Learning", "Statistics"],
            "learning_path": ["Learn ML basics", "Practice with datasets"],
            "timeline": "3-4 months"
        }
        mock_bot.career_agent.analyze_skill_gap.return_value = mock_analysis
        
        cmd = mock_bot.get_command('skill_gap')
        await cmd.callback(mock_ctx, input_text="Python, SQL | Data Scientist")
        
        # Verify skill gap analysis was called
        mock_bot.career_agent.analyze_skill_gap.assert_called_once()
        mock_ctx.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_skill_gap_command_invalid_format(self, mock_bot, mock_ctx):
        """Test skill gap analysis command with invalid format."""
        cmd = mock_bot.get_command('skill_gap')
        await cmd.callback(mock_ctx, input_text="Python, SQL, Data Scientist")  # Missing "|"
        
        # Should send format error
        mock_ctx.send.assert_called_once()
        call_args = mock_ctx.send.call_args[0][0]
        assert "format" in call_args.lower() and "❌" in call_args
    
    @pytest.mark.asyncio
    async def test_interview_next_command_no_session(self, mock_bot, mock_ctx):
        """Test interview_next command without active session."""
        cmd = mock_bot.get_command('interview_next')
        await cmd.callback(mock_ctx, answer="Sample answer")
        
        # Should indicate no active session
        mock_ctx.send.assert_called_once()
        call_args = mock_ctx.send.call_args[0][0]
        assert "no active" in call_args.lower() or "❌" in call_args
    
    @pytest.mark.asyncio
    async def test_interview_next_command_with_session(self, mock_bot, mock_ctx):
        """Test interview_next command with active session."""
        # Set up active session
        mock_bot.interview_sessions[mock_ctx.author.id] = {
            "role": "Software Engineer",
            "questions": ["Q1", "Q2", "Q3"],
            "current_question": 0,
            "answers": []
        }
        
        cmd = mock_bot.get_command('interview_next')
        await cmd.callback(mock_ctx, answer="My answer to question 1")
        
        # Should move to next question
        mock_ctx.send.assert_called_once()
        
        # Answer should be recorded
        session = mock_bot.interview_sessions[mock_ctx.author.id]
        assert len(session['answers']) == 1
        assert session['current_question'] == 1
    
    @pytest.mark.asyncio
    async def test_interview_end_command(self, mock_bot, mock_ctx):
        """Test interview_end command."""
        # Set up session with answers
        mock_bot.interview_sessions[mock_ctx.author.id] = {
            "session_id": "test_session",
            "role": "Software Engineer",
            "answers": ["Answer 1", "Answer 2"]
        }
        
        # Mock feedback response
        from career_agent import InterviewFeedback
        mock_feedback = InterviewFeedback(
            overall_performance=82.0,
            communication_skills=85.0,
            technical_knowledge=80.0,
            problem_solving=78.0,
            areas_for_improvement=["More examples"],
            suggested_practice_topics=["System design"]
        )
        mock_bot.career_agent.evaluate_interview_answers.return_value = mock_feedback
        
        cmd = mock_bot.get_command('interview_end')
        await cmd.callback(mock_ctx)
        
        # Verify feedback was generated and session cleaned up
        mock_bot.career_agent.evaluate_interview_answers.assert_called_once()
        mock_ctx.send.assert_called_once()
        assert mock_ctx.author.id not in mock_bot.interview_sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
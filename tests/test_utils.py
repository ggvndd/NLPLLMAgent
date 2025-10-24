"""
Unit tests for utility functions and validation.

Tests input validation, logging utilities, and helper functions.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.validators import InputValidator, ValidationResult, validate_discord_message_length
from utils.logger import setup_logger, LoggerMixin


class TestUtilityFunctions:
    """Test cases for utility functions and helpers."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and properties."""
        result = ValidationResult(
            is_valid=True,
            errors=["Error 1"],
            warnings=["Warning 1"]
        )
        
        assert result.is_valid
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
    
    def test_discord_message_validation_short(self):
        """Test Discord message validation for short messages."""
        message = "This is a short message"
        is_valid, processed = validate_discord_message_length(message)
        
        assert is_valid
        assert processed == message
    
    def test_discord_message_validation_long(self):
        """Test Discord message validation for long messages."""
        message = "A" * 2500  # Exceeds Discord limit
        is_valid, processed = validate_discord_message_length(message)
        
        assert not is_valid
        assert len(processed) <= 2000
        assert processed.endswith("...")
    
    def test_skill_extraction_from_text(self):
        """Test skill extraction functionality."""
        text = """
        I have experience with Python programming and JavaScript development.
        I also work with AWS cloud services and Docker containers.
        My background includes Machine Learning and Data Science projects.
        """
        
        skills = InputValidator.extract_skills_from_text(text)
        
        # Should find common technical skills
        assert len(skills) > 0
        # At least some of these should be found
        expected_skills = ["Python", "JavaScript", "AWS", "Docker", "Machine Learning", "Data Science"]
        found_skills = [skill for skill in expected_skills if skill in skills]
        assert len(found_skills) > 0
    
    def test_api_response_validation_valid(self):
        """Test API response validation with valid data."""
        response = {
            "status": "success",
            "data": {"key": "value"},
            "timestamp": "2024-01-01T00:00:00Z"
        }
        required_fields = ["status", "data"]
        
        result = InputValidator.validate_api_response(response, required_fields)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_api_response_validation_missing_fields(self):
        """Test API response validation with missing fields."""
        response = {
            "data": {"key": "value"}
        }
        required_fields = ["status", "data", "timestamp"]
        
        result = InputValidator.validate_api_response(response, required_fields)
        
        assert not result.is_valid
        assert "Missing required field: status" in result.errors
        assert "Missing required field: timestamp" in result.errors
    
    def test_api_response_validation_invalid_type(self):
        """Test API response validation with invalid type."""
        response = "This should be a dictionary"
        required_fields = ["status"]
        
        result = InputValidator.validate_api_response(response, required_fields)
        
        assert not result.is_valid
        assert "Response must be a dictionary" in result.errors


class TestLoggingUtilities:
    """Test cases for logging utilities."""
    
    def test_logger_setup(self):
        """Test logger setup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logger("test_logger", "DEBUG", temp_dir)
            
            assert logger.name == "test_logger"
            assert logger.level == 10  # DEBUG level
            assert len(logger.handlers) >= 2  # File and console handlers
    
    def test_logger_mixin(self):
        """Test LoggerMixin functionality."""
        class TestClass(LoggerMixin):
            def __init__(self):
                with tempfile.TemporaryDirectory() as temp_dir:
                    self.setup_logging("INFO", temp_dir)
        
        # Test that mixin methods work
        test_instance = TestClass()
        
        # These should not raise exceptions
        test_instance.log_info("Test info message")
        test_instance.log_warning("Test warning message")
        test_instance.log_debug("Test debug message")
        test_instance.log_error("Test error message")
    
    def test_logger_file_creation(self):
        """Test that logger creates log files correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logger("file_test", "INFO", temp_dir)
            logger.info("Test log message")
            
            # Check that log file was created
            log_file = os.path.join(temp_dir, "file_test.log")
            assert os.path.exists(log_file)
            
            # Check that log content was written
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test log message" in content


class TestAdvancedValidation:
    """Test cases for advanced validation scenarios."""
    
    def test_complex_skills_validation(self):
        """Test validation with complex skill scenarios."""
        # Test with various edge cases
        test_cases = [
            (["Python 3.8", "Machine Learning (ML)", "SQL Server"], True),
            (["", "Valid Skill"], False),  # Contains empty skill
            ([" Leading Space", "Trailing Space "], True),  # Whitespace issues
            (["Very " * 20 + "Long Skill Name"], True),  # Very long skill name
        ]
        
        for skills, should_be_valid in test_cases:
            result = InputValidator.validate_skills_list(skills)
            if should_be_valid:
                assert result.is_valid or len(result.warnings) > 0
            else:
                assert not result.is_valid
    
    def test_resume_content_analysis(self):
        """Test detailed resume content validation."""
        # Good resume with all sections
        good_resume = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        
        EXPERIENCE:
        Senior Software Engineer (2020-Present)
        - Developed web applications using Python and React
        - Led team of 5 developers on major project
        - Increased system performance by 40%
        
        EDUCATION:
        Bachelor of Science in Computer Science
        University of Technology (2016-2020)
        
        SKILLS:
        Python, JavaScript, React, SQL, Git, AWS
        """
        
        result = InputValidator.validate_resume_text(good_resume)
        assert result.is_valid
        # Should have minimal warnings for a well-structured resume
        
        # Poor resume missing key sections
        poor_resume = """
        Jane Smith
        I worked at a company for some time.
        I know some programming.
        """
        
        result = InputValidator.validate_resume_text(poor_resume)
        # Should have warnings about missing sections and contact info
        assert len(result.warnings) > 0
    
    def test_job_preferences_edge_cases(self):
        """Test job preferences validation with edge cases."""
        # Test various preference formats
        test_cases = [
            ({"location": "Remote", "salary": "50k-70k"}, True),
            ({"salary_range": "$80,000 - $120,000"}, True),
            ({"location": "", "industry": ""}, True),  # Empty but present
            ({"invalid_key": "value"}, True),  # Unknown keys are allowed
        ]
        
        for preferences, should_be_valid in test_cases:
            result = InputValidator.validate_job_preferences(preferences)
            if should_be_valid:
                assert result.is_valid
    
    def test_interview_answer_quality_check(self):
        """Test interview answer validation for quality indicators."""
        # Very short answers
        short_answers = ["Yes", "No", "Maybe"]
        result = InputValidator.validate_interview_answers(short_answers)
        assert result.is_valid  # Valid but should have warnings
        assert len(result.warnings) > 0
        
        # Very long answers
        long_answers = ["This is a " + "very " * 500 + "long answer"]
        result = InputValidator.validate_interview_answers(long_answers)
        assert result.is_valid
        assert any("very long" in warning for warning in result.warnings)
        
        # Good quality answers
        good_answers = [
            "I have three years of experience in software development, primarily working with Python and JavaScript.",
            "My approach to problem-solving involves breaking down complex issues into smaller, manageable components.",
            "I'm interested in this role because it aligns with my career goals and offers growth opportunities."
        ]
        result = InputValidator.validate_interview_answers(good_answers)
        assert result.is_valid
        # Should have minimal or no warnings for good answers


class TestErrorHandling:
    """Test cases for error handling and edge cases."""
    
    def test_input_sanitization_edge_cases(self):
        """Test input sanitization with various malicious inputs."""
        test_cases = [
            ("<script>alert('xss')</script>", False),  # Should remove script tags
            ("Normal text with <b>HTML</b> tags", False),  # Should remove HTML
            ("Text with\nmultiple\n\nline\nbreaks", True),  # Should normalize whitespace
            ("A" * 15000, True),  # Should truncate long input
        ]
        
        for input_text, should_contain_original in test_cases:
            sanitized = InputValidator.sanitize_user_input(input_text)
            
            if not should_contain_original:
                assert "<script>" not in sanitized
                assert "<b>" not in sanitized
            
            # All inputs should be sanitized to reasonable length
            assert len(sanitized) <= 10003  # 10000 + "..."
    
    def test_validation_with_none_inputs(self):
        """Test validation functions handle None inputs gracefully."""
        # These should not raise exceptions
        result = InputValidator.validate_skills_list(None or [])
        assert not result.is_valid
        
        sanitized = InputValidator.sanitize_user_input(None)
        assert sanitized == ""
        
        skills = InputValidator.extract_skills_from_text(None or "")
        assert isinstance(skills, list)
    
    def test_logger_error_handling(self):
        """Test logger handles errors gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with invalid log level
            logger = setup_logger("error_test", "INVALID_LEVEL", temp_dir)
            # Should default to INFO level without crashing
            assert logger.level == 20  # INFO level
            
            # Test logging with various message types
            logger.info("String message")
            logger.info(123)  # Number
            logger.info(None)  # None value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
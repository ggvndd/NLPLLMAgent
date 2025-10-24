"""
Input validation utilities for the Career Coach Agent.

Provides validation functions for user inputs, resume content, and API responses.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class InputValidator:
    """Validates various types of user input for the career agent."""
    
    @staticmethod
    def validate_skills_list(skills: List[str]) -> ValidationResult:
        """
        Validate a list of skills.
        
        Args:
            skills: List of skill strings
            
        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        warnings = []
        
        if not skills:
            errors.append("Skills list cannot be empty")
        
        if len(skills) > 50:
            warnings.append("Very large skills list - consider focusing on key skills")
        
        # Check for valid skill format
        for skill in skills:
            if not skill or not skill.strip():
                errors.append("Empty skill found in list")
                continue
                
            if len(skill) > 100:
                warnings.append(f"Very long skill name: '{skill[:50]}...'")
            
            # Check for common formatting issues
            if skill != skill.strip():
                warnings.append(f"Skill has leading/trailing whitespace: '{skill}'")
        
        # Check for duplicates
        lowercase_skills = [s.lower().strip() for s in skills]
        if len(lowercase_skills) != len(set(lowercase_skills)):
            warnings.append("Duplicate skills found")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_resume_text(resume_text: str, max_length: int = 10000) -> ValidationResult:
        """
        Validate resume text content.
        
        Args:
            resume_text: The resume content as text
            max_length: Maximum allowed length
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        if not resume_text or not resume_text.strip():
            errors.append("Resume text cannot be empty")
        
        if len(resume_text) > max_length:
            errors.append(f"Resume text too long ({len(resume_text)} chars, max {max_length})")
        
        if len(resume_text) < 100:
            warnings.append("Resume text seems very short - may not provide enough context")
        
        # Check for basic resume sections
        resume_lower = resume_text.lower()
        expected_sections = ['experience', 'education', 'skills']
        missing_sections = []
        
        for section in expected_sections:
            if section not in resume_lower:
                missing_sections.append(section)
        
        if missing_sections:
            warnings.append(f"Resume may be missing sections: {', '.join(missing_sections)}")
        
        # Check for contact information patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        if not re.search(email_pattern, resume_text):
            warnings.append("No email address found in resume")
        
        if not re.search(phone_pattern, resume_text):
            warnings.append("No phone number found in resume")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_job_preferences(preferences: Dict[str, Any]) -> ValidationResult:
        """
        Validate job preference dictionary.
        
        Args:
            preferences: Dictionary of job preferences
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Check for required keys
        recommended_keys = ['location', 'salary_range', 'industry', 'remote_ok']
        
        if not preferences:
            errors.append("Job preferences cannot be empty")
        
        # Validate salary range if provided
        if 'salary_range' in preferences:
            salary = preferences['salary_range']
            if isinstance(salary, str):
                # Try to extract numbers from salary string
                salary_numbers = re.findall(r'\d+', salary)
                if not salary_numbers:
                    warnings.append("Salary range format unclear - use format like '50k-70k' or '$50,000-$70,000'")
        
        # Validate location
        if 'location' in preferences:
            location = preferences['location']
            if isinstance(location, str) and len(location.strip()) == 0:
                warnings.append("Empty location preference")
        
        # Check for reasonable industry values
        if 'industry' in preferences:
            industry = preferences['industry']
            if isinstance(industry, str) and len(industry.strip()) == 0:
                warnings.append("Empty industry preference")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_interview_answers(answers: List[str]) -> ValidationResult:
        """
        Validate interview answers for evaluation.
        
        Args:
            answers: List of interview answers
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        if not answers:
            errors.append("No interview answers provided")
        
        for i, answer in enumerate(answers):
            if not answer or not answer.strip():
                errors.append(f"Answer {i+1} is empty")
                continue
            
            if len(answer) < 10:
                warnings.append(f"Answer {i+1} is very short - may not provide enough detail")
            
            if len(answer) > 2000:
                warnings.append(f"Answer {i+1} is very long - consider being more concise")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def validate_target_role(role: str) -> ValidationResult:
        """
        Validate a target role string.
        
        Args:
            role: Target role/job title
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        if not role or not role.strip():
            errors.append("Target role cannot be empty")
        
        if len(role) > 200:
            warnings.append("Target role name is very long")
        
        if len(role) < 3:
            warnings.append("Target role name seems too short")
        
        # Check for reasonable role format
        if role and role.islower():
            warnings.append("Role name should be properly capitalized")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """
        Sanitize user input by removing potentially harmful content.
        
        Args:
            text: Raw user input text
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove potential script tags or HTML
        text = re.sub(r'<[^>]*>', '', text)
        
        # Remove excessive special characters
        text = re.sub(r'[^\w\s\-.,!?()@#$%^&*+=;:\'\"\/\\]', '', text)
        
        # Limit length
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        return text
    
    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """
        Extract potential skills from text using pattern matching.
        
        Args:
            text: Text to analyze for skills
            
        Returns:
            List of extracted potential skills
        """
        # Common skill patterns
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|SQL|HTML|CSS|React|Vue|Angular)\b',
            r'\b(?:AWS|Azure|Docker|Kubernetes|Git|Linux|Windows|macOS)\b',
            r'\b(?:Machine Learning|Data Science|AI|Analytics|Statistics)\b',
            r'\b(?:Project Management|Agile|Scrum|Leadership|Communication)\b'
        ]
        
        skills = []
        text_upper = text.upper()
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend(matches)
        
        # Remove duplicates and return
        return list(set(skills))
    
    @staticmethod
    def validate_api_response(response: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
        """
        Validate API response structure.
        
        Args:
            response: API response dictionary
            required_fields: List of required field names
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        if not isinstance(response, dict):
            errors.append("Response must be a dictionary")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check for required fields
        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")
            elif response[field] is None:
                warnings.append(f"Field {field} is null")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


def validate_discord_message_length(message: str, max_length: int = 2000) -> Tuple[bool, str]:
    """
    Validate and truncate Discord message if needed.
    
    Args:
        message: Message to validate
        max_length: Maximum allowed length for Discord
        
    Returns:
        Tuple of (is_valid, processed_message)
    """
    if len(message) <= max_length:
        return True, message
    
    # Truncate with ellipsis
    truncated = message[:max_length-3] + "..."
    return False, truncated


def format_validation_errors(result: ValidationResult) -> str:
    """
    Format validation result into a readable string.
    
    Args:
        result: ValidationResult to format
        
    Returns:
        Formatted error/warning message
    """
    messages = []
    
    if result.errors:
        messages.append("❌ Errors:")
        for error in result.errors:
            messages.append(f"  • {error}")
    
    if result.warnings:
        messages.append("⚠️  Warnings:")
        for warning in result.warnings:
            messages.append(f"  • {warning}")
    
    return "\n".join(messages) if messages else "✅ Validation passed"
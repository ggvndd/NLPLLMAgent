"""
Career Coach LLM Agent

This module contains the core AI-powered career coaching functionality.
Provides career analysis, resume review, job matching, interview preparation,
and skill gap analysis capabilities.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from config import Config
from utils.logger import setup_logger


class AnalysisType(Enum):
    """Types of career analysis available."""
    CAREER_PATH = "career_path"
    RESUME_REVIEW = "resume_review"
    JOB_MATCHING = "job_matching"
    MOCK_INTERVIEW = "mock_interview"
    SKILL_GAP = "skill_gap"


@dataclass
class UserProfile:
    """Represents a user's career profile."""
    skills: List[str]
    experience: List[str]
    interests: List[str]
    education: List[str]
    career_goals: Optional[str] = None
    preferred_industries: Optional[List[str]] = None
    location_preferences: Optional[List[str]] = None
    salary_expectations: Optional[str] = None


@dataclass
class CareerRecommendation:
    """Represents a career recommendation."""
    job_title: str
    match_percentage: float
    required_skills: List[str]
    skill_gaps: List[str]
    salary_range: str
    career_path: List[str]
    reasoning: str


@dataclass
class ResumeAnalysis:
    """Represents resume analysis results."""
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    keyword_optimization: List[str]
    formatting_feedback: List[str]


@dataclass
class InterviewFeedback:
    """Represents mock interview feedback."""
    overall_performance: float
    communication_skills: float
    technical_knowledge: float
    problem_solving: float
    areas_for_improvement: List[str]
    suggested_practice_topics: List[str]


class CareerAgent:
    """
    AI-powered career coaching agent that provides comprehensive career guidance.
    
    Features:
    - Career path analysis and recommendations
    - Resume review and optimization suggestions
    - Job matching based on skills and preferences
    - Mock interview simulation with feedback
    - Skill gap analysis for target roles
    """
    
    def __init__(self, config: Config):
        """Initialize the career agent with configuration."""
        self.config = config
        self.logger = setup_logger(__name__, config.log_level)
        self.llm_client = self._initialize_llm_client()
        
        # Knowledge base for career guidance
        self.industry_data = self._load_industry_data()
        self.skill_categories = self._load_skill_categories()
        
        self.logger.info("Career Agent initialized successfully")
    
    def _initialize_llm_client(self):
        """Initialize the LLM client based on configuration."""
        try:
            if self.config.llm_provider == "demo":
                # Return None for demo mode - we'll use demo responses
                return None
            elif self.config.llm_provider == "openai":
                import openai
                return openai.OpenAI(api_key=self.config.openai_api_key)
            elif self.config.llm_provider == "anthropic":
                import anthropic
                return anthropic.Anthropic(api_key=self.config.anthropic_api_key)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM client: {e}")
            # Fallback to demo mode if initialization fails
            self.logger.info("Falling back to demo mode")
            return None
    
    def _load_industry_data(self) -> Dict[str, Any]:
        """Load industry and career data for analysis."""
        # In a real implementation, this would load from a database or external API
        return {
            "tech": {
                "roles": ["Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager"],
                "skills": ["Python", "JavaScript", "SQL", "Git", "AWS", "Docker"],
                "avg_salaries": {"entry": "70-90k", "mid": "90-130k", "senior": "130-200k+"}
            },
            "finance": {
                "roles": ["Financial Analyst", "Investment Banker", "Risk Manager", "Quantitative Analyst"],
                "skills": ["Excel", "Financial Modeling", "Python", "R", "Statistics"],
                "avg_salaries": {"entry": "60-80k", "mid": "80-120k", "senior": "120-250k+"}
            },
            "marketing": {
                "roles": ["Digital Marketer", "Content Manager", "SEO Specialist", "Growth Hacker"],
                "skills": ["Google Analytics", "SEO", "Social Media", "Content Creation", "A/B Testing"],
                "avg_salaries": {"entry": "45-65k", "mid": "65-95k", "senior": "95-150k+"}
            }
        }
    
    def _load_skill_categories(self) -> Dict[str, List[str]]:
        """Load skill categories for better analysis."""
        return {
            "technical": ["Python", "Java", "JavaScript", "SQL", "AWS", "Docker", "Git"],
            "analytical": ["Data Analysis", "Statistics", "Machine Learning", "Excel", "Tableau"],
            "communication": ["Public Speaking", "Writing", "Presentation", "Negotiation"],
            "leadership": ["Team Management", "Project Management", "Strategic Planning", "Mentoring"],
            "creative": ["Design", "Content Creation", "Photography", "Video Editing", "UX/UI"]
        }
    
    async def analyze_career_path(self, user_profile: UserProfile) -> List[CareerRecommendation]:
        """
        Analyze user profile and provide career path recommendations.
        
        Args:
            user_profile: User's skills, experience, and preferences
            
        Returns:
            List of career recommendations with match percentages and details
        """
        self.logger.info(f"Analyzing career path for user with {len(user_profile.skills)} skills")
        
        try:
            # Create prompt for LLM analysis
            prompt = self._create_career_analysis_prompt(user_profile)
            
            # Get LLM response
            llm_response = await self._call_llm(prompt, AnalysisType.CAREER_PATH)
            
            # Parse and structure the recommendations
            recommendations = self._parse_career_recommendations(llm_response, user_profile)
            
            self.logger.info(f"Generated {len(recommendations)} career recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in career path analysis: {e}")
            raise
    
    async def review_resume(self, resume_text: str, target_role: Optional[str] = None) -> ResumeAnalysis:
        """
        Analyze resume and provide improvement suggestions.
        
        Args:
            resume_text: The resume content as text
            target_role: Optional target role for focused feedback
            
        Returns:
            Detailed resume analysis with scores and suggestions
        """
        self.logger.info("Analyzing resume for improvement suggestions")
        
        try:
            prompt = self._create_resume_review_prompt(resume_text, target_role)
            llm_response = await self._call_llm(prompt, AnalysisType.RESUME_REVIEW)
            
            analysis = self._parse_resume_analysis(llm_response)
            
            self.logger.info(f"Resume analysis completed with score: {analysis.overall_score}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in resume review: {e}")
            raise
    
    async def match_jobs(self, user_profile: UserProfile, job_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find job opportunities that match user profile and preferences.
        
        Args:
            user_profile: User's skills and experience
            job_preferences: Location, salary, industry preferences
            
        Returns:
            List of matching job opportunities with fit scores
        """
        self.logger.info("Matching jobs based on user profile and preferences")
        
        try:
            prompt = self._create_job_matching_prompt(user_profile, job_preferences)
            llm_response = await self._call_llm(prompt, AnalysisType.JOB_MATCHING)
            
            matches = self._parse_job_matches(llm_response)
            
            self.logger.info(f"Found {len(matches)} job matches")
            return matches
            
        except Exception as e:
            self.logger.error(f"Error in job matching: {e}")
            raise
    
    async def conduct_mock_interview(self, role: str, questions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Conduct a mock interview simulation.
        
        Args:
            role: Target role for the interview
            questions: Optional custom questions (auto-generated if not provided)
            
        Returns:
            Interview session data with questions and evaluation framework
        """
        self.logger.info(f"Starting mock interview for {role}")
        
        try:
            if not questions:
                questions = await self._generate_interview_questions(role)
            
            interview_session = {
                "role": role,
                "questions": questions,
                "start_time": datetime.now().isoformat(),
                "session_id": f"interview_{int(datetime.now().timestamp())}"
            }
            
            self.logger.info(f"Mock interview session created with {len(questions)} questions")
            return interview_session
            
        except Exception as e:
            self.logger.error(f"Error creating mock interview: {e}")
            raise
    
    async def evaluate_interview_answers(self, session_id: str, answers: List[str]) -> InterviewFeedback:
        """
        Evaluate interview answers and provide feedback.
        
        Args:
            session_id: Interview session identifier
            answers: List of user answers to interview questions
            
        Returns:
            Detailed feedback on interview performance
        """
        self.logger.info(f"Evaluating interview answers for session {session_id}")
        
        try:
            prompt = self._create_interview_evaluation_prompt(answers)
            llm_response = await self._call_llm(prompt, AnalysisType.MOCK_INTERVIEW)
            
            feedback = self._parse_interview_feedback(llm_response)
            
            self.logger.info(f"Interview evaluation completed with score: {feedback.overall_performance}")
            return feedback
            
        except Exception as e:
            self.logger.error(f"Error evaluating interview: {e}")
            raise
    
    async def analyze_skill_gap(self, current_skills: List[str], target_role: str) -> Dict[str, Any]:
        """
        Analyze skill gaps for a target role.
        
        Args:
            current_skills: User's current skills
            target_role: Desired career role
            
        Returns:
            Skill gap analysis with learning recommendations
        """
        self.logger.info(f"Analyzing skill gap for target role: {target_role}")
        
        try:
            prompt = self._create_skill_gap_prompt(current_skills, target_role)
            llm_response = await self._call_llm(prompt, AnalysisType.SKILL_GAP)
            
            analysis = self._parse_skill_gap_analysis(llm_response)
            
            self.logger.info(f"Skill gap analysis completed for {target_role}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in skill gap analysis: {e}")
            raise
    
    async def _call_llm(self, prompt: str, analysis_type: AnalysisType) -> str:
        """Make API call to the configured LLM."""
        try:
            # Use demo mode if configured or if no client available
            if self.config.llm_provider == "demo" or self.llm_client is None:
                self.logger.info("Using demo response (no API key configured)")
                return self._get_demo_response(analysis_type)
            
            # Check for missing API keys
            if (self.config.llm_provider == "openai" and not self.config.openai_api_key) or \
               (self.config.llm_provider == "anthropic" and not self.config.anthropic_api_key):
                self.logger.info("API key missing, using demo response")
                return self._get_demo_response(analysis_type)
            
            # Real API calls (will be implemented when you have API keys)
            if self.config.llm_provider == "openai":
                # OpenAI API call would go here
                # For now, fall back to demo
                self.logger.info("OpenAI API not implemented in demo, using demo response")
                return self._get_demo_response(analysis_type)
            
            elif self.config.llm_provider == "anthropic":
                # Anthropic API call would go here  
                # For now, fall back to demo
                self.logger.info("Anthropic API not implemented in demo, using demo response")
                return self._get_demo_response(analysis_type)
            
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
                
        except Exception as e:
            self.logger.error(f"LLM API call failed: {e}")
            # Fallback to demo response if API call fails
            self.logger.info("Falling back to demo response")
            return self._get_demo_response(analysis_type)
    
    def _create_career_analysis_prompt(self, user_profile: UserProfile) -> str:
        """Create prompt for career path analysis."""
        return f"""
        Analyze this user's profile and provide 3-5 career recommendations:
        
        Skills: {', '.join(user_profile.skills)}
        Experience: {', '.join(user_profile.experience)}
        Interests: {', '.join(user_profile.interests)}
        Education: {', '.join(user_profile.education)}
        Career Goals: {user_profile.career_goals or 'Not specified'}
        
        For each recommendation, provide:
        1. Job title and match percentage (0-100%)
        2. Required skills and skill gaps
        3. Salary range
        4. Career progression path
        5. Reasoning for the match
        
        Format as JSON array with structured data.
        """
    
    def _create_resume_review_prompt(self, resume_text: str, target_role: Optional[str]) -> str:
        """Create prompt for resume review."""
        role_context = f" for a {target_role} position" if target_role else ""
        return f"""
        Review this resume{role_context} and provide detailed feedback:
        
        Resume Content:
        {resume_text}
        
        Provide analysis including:
        1. Overall score (0-100)
        2. Key strengths (3-5 points)
        3. Areas for improvement (3-5 points)
        4. Specific suggestions for enhancement
        5. Keywords to add for better ATS compatibility
        6. Formatting and structure feedback
        
        Format as structured JSON with clear sections.
        """
    
    def _create_job_matching_prompt(self, user_profile: UserProfile, preferences: Dict[str, Any]) -> str:
        """Create prompt for job matching."""
        return f"""
        Find job opportunities matching this profile:
        
        User Skills: {', '.join(user_profile.skills)}
        Experience: {', '.join(user_profile.experience)}
        Preferences: {json.dumps(preferences)}
        
        Provide 5-7 job matches including:
        1. Job title and company type
        2. Match percentage
        3. Key requirements
        4. Why it's a good fit
        5. Estimated salary range
        6. Remote/location options
        
        Format as JSON array.
        """
    
    async def _generate_interview_questions(self, role: str) -> List[str]:
        """Generate interview questions for a specific role."""
        prompt = f"""
        Generate 8-10 interview questions for a {role} position.
        Include a mix of:
        1. Behavioral questions (2-3)
        2. Technical/skill-based questions (3-4)
        3. Situational questions (2-3)
        4. Culture fit questions (1-2)
        
        Return as JSON array of strings.
        """
        
        response = await self._call_llm(prompt, AnalysisType.MOCK_INTERVIEW)
        return json.loads(response)
    
    def _create_interview_evaluation_prompt(self, answers: List[str]) -> str:
        """Create prompt for interview evaluation."""
        formatted_answers = '\n'.join([f"Q{i+1}: {answer}" for i, answer in enumerate(answers)])
        
        return f"""
        Evaluate these interview answers and provide scores (0-100) for:
        
        Interview Answers:
        {formatted_answers}
        
        Scoring criteria:
        1. Overall performance
        2. Communication skills
        3. Technical knowledge demonstration
        4. Problem-solving approach
        5. Areas for improvement
        6. Suggested practice topics
        
        Format as structured JSON with numerical scores and detailed feedback.
        """
    
    def _create_skill_gap_prompt(self, current_skills: List[str], target_role: str) -> str:
        """Create prompt for skill gap analysis."""
        return f"""
        Analyze skill gaps for career transition:
        
        Current Skills: {', '.join(current_skills)}
        Target Role: {target_role}
        
        Provide:
        1. Skills already possessed that are relevant
        2. Critical skills missing for the role
        3. Nice-to-have skills for competitive advantage
        4. Learning path with priorities
        5. Estimated timeline for skill development
        6. Recommended resources and courses
        
        Format as structured JSON with clear categories.
        """
    
    def _parse_career_recommendations(self, llm_response: str, user_profile: UserProfile) -> List[CareerRecommendation]:
        """Parse LLM response into structured career recommendations."""
        try:
            data = json.loads(llm_response)
            recommendations = []
            
            for item in data:
                rec = CareerRecommendation(
                    job_title=item.get('job_title', ''),
                    match_percentage=item.get('match_percentage', 0),
                    required_skills=item.get('required_skills', []),
                    skill_gaps=item.get('skill_gaps', []),
                    salary_range=item.get('salary_range', ''),
                    career_path=item.get('career_path', []),
                    reasoning=item.get('reasoning', '')
                )
                recommendations.append(rec)
            
            return recommendations
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse LLM response as JSON, creating fallback recommendations")
            return self._create_fallback_recommendations(user_profile)
    
    def _parse_resume_analysis(self, llm_response: str) -> ResumeAnalysis:
        """Parse LLM response into structured resume analysis."""
        try:
            data = json.loads(llm_response)
            return ResumeAnalysis(
                overall_score=data.get('overall_score', 0),
                strengths=data.get('strengths', []),
                weaknesses=data.get('weaknesses', []),
                improvement_suggestions=data.get('improvement_suggestions', []),
                keyword_optimization=data.get('keyword_optimization', []),
                formatting_feedback=data.get('formatting_feedback', [])
            )
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse resume analysis, returning default")
            return ResumeAnalysis(
                overall_score=75,
                strengths=["Clear structure", "Relevant experience"],
                weaknesses=["Could use more metrics", "Missing key skills"],
                improvement_suggestions=["Add quantifiable achievements", "Update skills section"],
                keyword_optimization=["Add industry keywords", "Include technical skills"],
                formatting_feedback=["Use consistent formatting", "Improve readability"]
            )
    
    def _parse_job_matches(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into job matches."""
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse job matches, returning empty list")
            return []
    
    def _parse_interview_feedback(self, llm_response: str) -> InterviewFeedback:
        """Parse LLM response into interview feedback."""
        try:
            data = json.loads(llm_response)
            return InterviewFeedback(
                overall_performance=data.get('overall_performance', 0),
                communication_skills=data.get('communication_skills', 0),
                technical_knowledge=data.get('technical_knowledge', 0),
                problem_solving=data.get('problem_solving', 0),
                areas_for_improvement=data.get('areas_for_improvement', []),
                suggested_practice_topics=data.get('suggested_practice_topics', [])
            )
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse interview feedback, returning default")
            return InterviewFeedback(
                overall_performance=75,
                communication_skills=80,
                technical_knowledge=70,
                problem_solving=75,
                areas_for_improvement=["Technical depth", "Specific examples"],
                suggested_practice_topics=["System design", "Behavioral questions"]
            )
    
    def _parse_skill_gap_analysis(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into skill gap analysis."""
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse skill gap analysis, returning default")
            return {
                "relevant_skills": [],
                "missing_skills": [],
                "learning_path": [],
                "timeline": "3-6 months",
                "resources": []
            }
    
    def _get_demo_response(self, analysis_type: AnalysisType) -> str:
        """Get demo response when API is not available."""
        demo_responses = {
            AnalysisType.CAREER_PATH: '''[
                {
                    "job_title": "Software Engineer",
                    "match_percentage": 85,
                    "required_skills": ["Python", "JavaScript", "Git"],
                    "skill_gaps": ["React", "Docker"],
                    "salary_range": "$70k-110k",
                    "career_path": ["Junior Developer", "Software Engineer", "Senior Engineer"],
                    "reasoning": "Strong foundation in programming languages with room for frontend and DevOps skills"
                },
                {
                    "job_title": "Data Analyst",
                    "match_percentage": 75,
                    "required_skills": ["Python", "SQL", "Excel"],
                    "skill_gaps": ["Tableau", "Statistics"],
                    "salary_range": "$60k-90k",
                    "career_path": ["Data Analyst", "Senior Data Analyst", "Data Scientist"],
                    "reasoning": "Good analytical skills foundation, need to develop visualization and statistics"
                }
            ]''',
            AnalysisType.RESUME_REVIEW: '''{
                "overall_score": 75,
                "strengths": ["Clear technical skills section", "Relevant work experience", "Good formatting"],
                "weaknesses": ["Missing quantified achievements", "No leadership examples", "Lacks keywords"],
                "improvement_suggestions": ["Add metrics to achievements", "Include soft skills", "Optimize for ATS"],
                "keyword_optimization": ["Add cloud technologies", "Include frameworks", "Add certifications"],
                "formatting_feedback": ["Use consistent bullet points", "Add contact information", "Improve spacing"]
            }''',
            AnalysisType.JOB_MATCHING: '''[
                {
                    "job_title": "Python Developer",
                    "company_type": "Tech Startup",
                    "match_percentage": 90,
                    "salary_range": "$80k-120k",
                    "location": "Remote",
                    "requirements": ["Python", "FastAPI", "PostgreSQL"]
                },
                {
                    "job_title": "Backend Engineer",
                    "company_type": "Mid-size Company",
                    "match_percentage": 85,
                    "salary_range": "$75k-115k",
                    "location": "Hybrid",
                    "requirements": ["Python", "Django", "AWS"]
                }
            ]''',
            AnalysisType.MOCK_INTERVIEW: '''[
                "Tell me about yourself and your background",
                "What interests you about this role?",
                "Describe a challenging project you worked on",
                "How do you handle debugging complex issues?",
                "Where do you see yourself in 5 years?"
            ]''',
            AnalysisType.SKILL_GAP: '''{
                "relevant_skills": ["Python", "SQL"],
                "missing_skills": ["Machine Learning", "Statistics", "Pandas"],
                "learning_path": ["Learn statistics fundamentals", "Master pandas and numpy", "Practice ML algorithms", "Work on real projects"],
                "timeline": "4-6 months with consistent practice",
                "resources": ["Online courses", "Kaggle competitions", "Open source projects"]
            }'''
        }
        
        return demo_responses.get(analysis_type, '{"message": "Demo response not available for this analysis type"}')
    
    def _create_fallback_recommendations(self, user_profile: UserProfile) -> List[CareerRecommendation]:
        """Create fallback recommendations when LLM parsing fails."""
        # Simple matching based on skills
        recommendations = []
        
        for industry, data in self.industry_data.items():
            skill_matches = set(user_profile.skills).intersection(set(data["skills"]))
            if skill_matches:
                match_percentage = (len(skill_matches) / len(data["skills"])) * 100
                
                rec = CareerRecommendation(
                    job_title=data["roles"][0],  # Use first role as example
                    match_percentage=match_percentage,
                    required_skills=data["skills"],
                    skill_gaps=list(set(data["skills"]) - set(user_profile.skills)),
                    salary_range=data["avg_salaries"]["mid"],
                    career_path=[f"Junior {data['roles'][0]}", data["roles"][0], f"Senior {data['roles'][0]}"],
                    reasoning=f"Good match based on {len(skill_matches)} matching skills in {industry}"
                )
                recommendations.append(rec)
        
        return recommendations[:3]  # Return top 3


# CLI interface for testing
async def main():
    """Main function for CLI testing."""
    config = Config()
    agent = CareerAgent(config)
    
    # Example usage
    user_profile = UserProfile(
        skills=["Python", "Data Analysis", "SQL", "Machine Learning"],
        experience=["2 years software development", "1 year data analysis"],
        interests=["AI", "Data Science", "Technology"],
        education=["Bachelor's Computer Science"],
        career_goals="Become a senior data scientist"
    )
    
    print("🤖 Career Coach Agent - CLI Mode")
    print("=" * 40)
    
    # Career path analysis
    print("\n📊 Analyzing career paths...")
    recommendations = await agent.analyze_career_path(user_profile)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec.job_title} ({rec.match_percentage}% match)")
        print(f"   Salary: {rec.salary_range}")
        print(f"   Skills needed: {', '.join(rec.skill_gaps[:3])}")
        print(f"   Reasoning: {rec.reasoning[:100]}...")
    
    print("\n✅ Career analysis complete!")
    print("💡 Use Discord bot for interactive coaching: python src/discord_bot.py")


if __name__ == "__main__":
    asyncio.run(main())
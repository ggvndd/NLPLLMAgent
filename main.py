"""
Main CLI interface for the Career Coach Agent.

Provides command-line access to career coaching features without Discord.
Useful for testing, development, and direct API usage.
"""

import asyncio
import argparse
import sys
import os
import json
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.career_agent import CareerAgent, UserProfile
from src.config import Config
from src.utils.logger import setup_logger
from src.utils.validators import InputValidator, format_validation_errors


class CareerCoachCLI:
    """Command-line interface for the Career Coach Agent."""
    
    def __init__(self):
        """Initialize CLI with configuration and agent."""
        try:
            self.config = Config()
            self.agent = CareerAgent(self.config)
            self.logger = setup_logger("cli", self.config.log_level)
        except Exception as e:
            print(f"❌ Error initializing Career Coach: {e}")
            print("💡 Make sure you have created a .env file with required API keys")
            sys.exit(1)
    
    def print_banner(self):
        """Print welcome banner."""
        print("=" * 60)
        print("🤖 AI-Powered Career Coach Agent - CLI Mode")
        print("=" * 60)
        print(f"📊 LLM Provider: {self.config.llm_provider}")
        print(f"📝 Log Level: {self.config.log_level}")
        print("-" * 60)
    
    async def analyze_career_paths(self, skills: List[str]) -> None:
        """Analyze career paths based on skills."""
        print(f"\n📊 Analyzing career paths for skills: {', '.join(skills)}")
        print("-" * 50)
        
        try:
            # Validate input
            validation = InputValidator.validate_skills_list(skills)
            if not validation.is_valid:
                print("❌ Input validation failed:")
                print(format_validation_errors(validation))
                return
            
            # Create user profile
            profile = UserProfile(
                skills=skills,
                experience=[],
                interests=[],
                education=[]
            )
            
            # Get recommendations
            recommendations = await self.agent.analyze_career_path(profile)
            
            # Display results
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec.job_title}")
                print(f"   Match: {rec.match_percentage:.0f}%")
                print(f"   Salary: {rec.salary_range}")
                print(f"   Skills to develop: {', '.join(rec.skill_gaps[:3])}")
                print(f"   Career path: {' → '.join(rec.career_path)}")
                print(f"   Why: {rec.reasoning[:100]}...")
            
            print(f"\n✅ Analysis complete! Found {len(recommendations)} career recommendations.")
            
        except Exception as e:
            print(f"❌ Error during career analysis: {e}")
            self.logger.error(f"Career analysis error: {e}")
    
    async def review_resume(self, resume_file: str, target_role: Optional[str] = None) -> None:
        """Review resume from file."""
        print(f"\n📄 Reviewing resume: {resume_file}")
        if target_role:
            print(f"🎯 Target role: {target_role}")
        print("-" * 50)
        
        try:
            # Read resume file
            if not os.path.exists(resume_file):
                print(f"❌ Resume file not found: {resume_file}")
                return
            
            with open(resume_file, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            
            # Validate resume
            validation = InputValidator.validate_resume_text(resume_text)
            if not validation.is_valid:
                print("❌ Resume validation failed:")
                print(format_validation_errors(validation))
                return
            
            # Analyze resume
            analysis = await self.agent.review_resume(resume_text, target_role)
            
            # Display results
            print(f"\n📊 Overall Score: {analysis.overall_score:.0f}/100")
            
            if analysis.strengths:
                print("\n✅ Strengths:")
                for strength in analysis.strengths:
                    print(f"   • {strength}")
            
            if analysis.improvement_suggestions:
                print("\n🔧 Improvement Suggestions:")
                for suggestion in analysis.improvement_suggestions:
                    print(f"   • {suggestion}")
            
            if analysis.keyword_optimization:
                print("\n🔍 Keyword Optimization:")
                for keyword in analysis.keyword_optimization:
                    print(f"   • {keyword}")
            
            print(f"\n✅ Resume review complete!")
            
        except Exception as e:
            print(f"❌ Error during resume review: {e}")
            self.logger.error(f"Resume review error: {e}")
    
    async def match_jobs(self, skills: List[str], preferences: str) -> None:
        """Match jobs based on skills and preferences."""
        print(f"\n🎯 Matching jobs for: {', '.join(skills)}")
        print(f"📋 Preferences: {preferences}")
        print("-" * 50)
        
        try:
            # Parse preferences
            pref_dict = {}
            for pref in preferences.split(','):
                pref = pref.strip()
                if '$' in pref or 'k' in pref.lower():
                    pref_dict['salary_range'] = pref
                elif 'remote' in pref.lower():
                    pref_dict['remote_ok'] = True
                else:
                    pref_dict.setdefault('keywords', []).append(pref)
            
            # Create user profile
            profile = UserProfile(
                skills=skills,
                experience=[],
                interests=[],
                education=[]
            )
            
            # Get job matches
            matches = await self.agent.match_jobs(profile, pref_dict)
            
            # Display results
            for i, match in enumerate(matches, 1):
                print(f"\n{i}. {match.get('job_title', 'Job Opportunity')}")
                print(f"   Company: {match.get('company_type', 'Various')}")
                print(f"   Match: {match.get('match_percentage', 85):.0f}%")
                print(f"   Salary: {match.get('salary_range', 'Competitive')}")
                print(f"   Location: {match.get('location', 'Multiple locations')}")
            
            print(f"\n✅ Job matching complete! Found {len(matches)} opportunities.")
            
        except Exception as e:
            print(f"❌ Error during job matching: {e}")
            self.logger.error(f"Job matching error: {e}")
    
    async def skill_gap_analysis(self, current_skills: List[str], target_role: str) -> None:
        """Analyze skill gaps for target role."""
        print(f"\n🎯 Skill gap analysis for: {target_role}")
        print(f"🔧 Current skills: {', '.join(current_skills)}")
        print("-" * 50)
        
        try:
            # Analyze skill gap
            analysis = await self.agent.analyze_skill_gap(current_skills, target_role)
            
            # Display results
            if analysis.get('relevant_skills'):
                print("\n✅ Skills you have:")
                for skill in analysis['relevant_skills']:
                    print(f"   • {skill}")
            
            if analysis.get('missing_skills'):
                print("\n📚 Skills to develop:")
                for skill in analysis['missing_skills']:
                    print(f"   • {skill}")
            
            if analysis.get('learning_path'):
                print("\n🗺️ Learning path:")
                for i, step in enumerate(analysis['learning_path'], 1):
                    print(f"   {i}. {step}")
            
            timeline = analysis.get('timeline', '3-6 months')
            print(f"\n⏱️ Estimated timeline: {timeline}")
            
            print(f"\n✅ Skill gap analysis complete!")
            
        except Exception as e:
            print(f"❌ Error during skill gap analysis: {e}")
            self.logger.error(f"Skill gap analysis error: {e}")
    
    def interactive_mode(self):
        """Run interactive CLI mode."""
        print("\n🎮 Interactive Mode - Choose an option:")
        print("1. Analyze career paths")
        print("2. Review resume")
        print("3. Match jobs")
        print("4. Skill gap analysis")
        print("5. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    skills_input = input("Enter your skills (comma-separated): ").strip()
                    skills = [s.strip() for s in skills_input.split(',')]
                    asyncio.run(self.analyze_career_paths(skills))
                
                elif choice == '2':
                    resume_file = input("Enter resume file path: ").strip()
                    target_role = input("Enter target role (optional): ").strip() or None
                    asyncio.run(self.review_resume(resume_file, target_role))
                
                elif choice == '3':
                    skills_input = input("Enter your skills (comma-separated): ").strip()
                    skills = [s.strip() for s in skills_input.split(',')]
                    preferences = input("Enter job preferences (comma-separated): ").strip()
                    asyncio.run(self.match_jobs(skills, preferences))
                
                elif choice == '4':
                    skills_input = input("Enter current skills (comma-separated): ").strip()
                    skills = [s.strip() for s in skills_input.split(',')]
                    target_role = input("Enter target role: ").strip()
                    asyncio.run(self.skill_gap_analysis(skills, target_role))
                
                elif choice == '5':
                    print("\n👋 Thank you for using Career Coach! Good luck with your career journey!")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Career Coach Agent - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --interactive                    # Interactive mode
  python main.py --analyze "Python,SQL,Git"      # Analyze career paths
  python main.py --resume resume.txt              # Review resume
  python main.py --jobs "Python,AWS" "Remote,Tech,80k+"  # Match jobs
  python main.py --skills "Python,SQL" --role "Data Scientist"  # Skill gap
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--analyze', '-a', metavar='SKILLS',
                       help='Analyze career paths for comma-separated skills')
    parser.add_argument('--resume', '-r', metavar='FILE',
                       help='Review resume from file')
    parser.add_argument('--target-role', '-t', metavar='ROLE',
                       help='Target role for resume review')
    parser.add_argument('--jobs', '-j', nargs=2, metavar=('SKILLS', 'PREFERENCES'),
                       help='Match jobs: skills and preferences')
    parser.add_argument('--skills', '-s', metavar='SKILLS',
                       help='Current skills for skill gap analysis')
    parser.add_argument('--role', metavar='ROLE',
                       help='Target role for skill gap analysis')
    
    args = parser.parse_args()
    
    # Initialize CLI
    try:
        cli = CareerCoachCLI()
        cli.print_banner()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return 1
    
    # Handle arguments
    if args.interactive:
        cli.interactive_mode()
    
    elif args.analyze:
        skills = [s.strip() for s in args.analyze.split(',')]
        asyncio.run(cli.analyze_career_paths(skills))
    
    elif args.resume:
        asyncio.run(cli.review_resume(args.resume, args.target_role))
    
    elif args.jobs:
        skills = [s.strip() for s in args.jobs[0].split(',')]
        preferences = args.jobs[1]
        asyncio.run(cli.match_jobs(skills, preferences))
    
    elif args.skills and args.role:
        skills = [s.strip() for s in args.skills.split(',')]
        asyncio.run(cli.skill_gap_analysis(skills, args.role))
    
    else:
        # Default to interactive mode if no arguments
        print("💡 No arguments provided. Starting interactive mode...")
        cli.interactive_mode()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
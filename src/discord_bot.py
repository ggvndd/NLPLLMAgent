"""
Discord Bot Integration for Career Coach Agent.

Provides Discord bot functionality for interactive career coaching through 
chat commands, including career analysis, resume review, job matching, 
and mock interviews.
"""

import asyncio
import io
import json
import logging
import traceback
from typing import Optional, List, Dict, Any

import discord
from discord.ext import commands

from config import Config
from career_agent import CareerAgent, UserProfile, AnalysisType
from utils.logger import setup_logger
from utils.validators import (
    InputValidator, validate_discord_message_length, 
    format_validation_errors
)


class CareerCoachBot(commands.Bot):
    """
    Discord bot for AI-powered career coaching.
    
    Provides interactive career guidance through Discord commands including:
    - Career path analysis
    - Resume review and feedback  
    - Job matching recommendations
    - Mock interview simulations
    - Skill gap analysis
    """
    
    def __init__(self, config: Config):
        """Initialize the Discord bot with career agent integration."""
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        # Initialize bot with command prefix
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
        
        self.config = config
        self.career_agent = CareerAgent(config)
        self.logger = setup_logger(__name__, config.log_level)
        
        # Store user sessions for mock interviews
        self.interview_sessions: Dict[int, Dict] = {}
        
        self.logger.info("Career Coach Discord Bot initialized")
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        self.logger.info(f'Bot is ready! Logged in as {self.user.name} (ID: {self.user.id})')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="!help for career coaching"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors gracefully."""
        self.logger.error(f"Command error in {ctx.command}: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Command not found. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
        else:
            await ctx.send("❌ An error occurred while processing your command. Please try again.")
            # Log the full traceback for debugging
            self.logger.error(f"Unexpected error: {traceback.format_exc()}")


# Create bot instance
def create_bot(config: Config) -> CareerCoachBot:
    """Create and configure the Discord bot."""
    bot = CareerCoachBot(config)
    
    @bot.command(name='help')
    async def help_command(ctx):
        """Show available commands and usage information."""
        embed = discord.Embed(
            title="🤖 Career Coach Bot - Commands",
            description="AI-powered career guidance and coaching",
            color=0x00ff00
        )
        
        commands_info = [
            ("!career_analyze <skills>", "Analyze career paths based on your skills\n*Example: !career_analyze Python, Machine Learning, Data Analysis*"),
            ("!resume_review", "Get resume improvement suggestions (attach your resume as .txt file)"),
            ("!job_match <preferences>", "Find matching job opportunities\n*Example: !job_match Remote, Tech, $80k+*"),
            ("!mock_interview <role>", "Start a mock interview simulation\n*Example: !mock_interview Software Engineer*"),
            ("!skill_gap <current_skills> | <target_role>", "Analyze skills needed for target role\n*Example: !skill_gap Python, SQL | Data Scientist*"),
            ("!profile_create", "Create your career profile for personalized recommendations"),
            ("!help", "Show this help message")
        ]
        
        for name, description in commands_info:
            embed.add_field(name=name, value=description, inline=False)
        
        embed.add_field(
            name="💡 Tips",
            value="• Use quotes for multi-word inputs: `\"Software Engineer\"`\n• Attach resume as .txt file for review\n• Be specific with your preferences for better matches",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @bot.command(name='career_analyze')
    async def career_analyze(ctx, *, skills_input: str):
        """Analyze career paths based on user skills."""
        try:
            # Validate input
            skills_list = [skill.strip() for skill in skills_input.split(',')]
            validation_result = InputValidator.validate_skills_list(skills_list)
            
            if not validation_result.is_valid:
                error_msg = format_validation_errors(validation_result)
                await ctx.send(f"❌ Input validation failed:\n```{error_msg}```")
                return
            
            # Show typing indicator
            async with ctx.typing():
                # Create user profile
                user_profile = UserProfile(
                    skills=skills_list,
                    experience=[],
                    interests=[],
                    education=[]
                )
                
                # Get career recommendations
                recommendations = await bot.career_agent.analyze_career_path(user_profile)
            
            # Format response
            embed = discord.Embed(
                title="📊 Career Path Analysis",
                description=f"Based on your skills: {', '.join(skills_list[:5])}",
                color=0x0099ff
            )
            
            for i, rec in enumerate(recommendations[:3], 1):
                field_value = (
                    f"**Match:** {rec.match_percentage:.0f}%\n"
                    f"**Salary:** {rec.salary_range}\n"
                    f"**Skills to develop:** {', '.join(rec.skill_gaps[:3])}\n"
                    f"**Why:** {rec.reasoning[:100]}..."
                )
                embed.add_field(
                    name=f"{i}. {rec.job_title}",
                    value=field_value,
                    inline=False
                )
            
            embed.set_footer(text="Use !skill_gap for detailed skill development plan")
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error in career_analyze: {e}")
            await ctx.send("❌ Sorry, I encountered an error analyzing your career path. Please try again.")
    
    @bot.command(name='resume_review')
    async def resume_review(ctx):
        """Review resume from attached file."""
        try:
            # Check for attachments
            if not ctx.message.attachments:
                await ctx.send("📄 Please attach your resume as a .txt file and run the command again.")
                return
            
            attachment = ctx.message.attachments[0]
            
            # Validate file type and size
            if not attachment.filename.lower().endswith('.txt'):
                await ctx.send("❌ Please attach a .txt file. Convert your resume to plain text format.")
                return
            
            if attachment.size > 50000:  # 50KB limit
                await ctx.send("❌ File too large. Please ensure your resume is under 50KB.")
                return
            
            # Download and read file
            async with ctx.typing():
                file_content = await attachment.read()
                resume_text = file_content.decode('utf-8', errors='ignore')
                
                # Validate resume content
                validation_result = InputValidator.validate_resume_text(resume_text)
                if not validation_result.is_valid:
                    error_msg = format_validation_errors(validation_result)
                    await ctx.send(f"❌ Resume validation failed:\n```{error_msg}```")
                    return
                
                # Analyze resume
                analysis = await bot.career_agent.review_resume(resume_text)
            
            # Format response
            embed = discord.Embed(
                title="📋 Resume Analysis Results",
                description=f"Overall Score: **{analysis.overall_score:.0f}/100**",
                color=0x00ff00 if analysis.overall_score >= 80 else 0xffaa00 if analysis.overall_score >= 60 else 0xff0000
            )
            
            # Strengths
            if analysis.strengths:
                embed.add_field(
                    name="✅ Strengths",
                    value='\n'.join([f"• {s}" for s in analysis.strengths[:3]]),
                    inline=False
                )
            
            # Improvement areas
            if analysis.improvement_suggestions:
                embed.add_field(
                    name="🔧 Improvement Suggestions",
                    value='\n'.join([f"• {s}" for s in analysis.improvement_suggestions[:3]]),
                    inline=False
                )
            
            # Keywords
            if analysis.keyword_optimization:
                embed.add_field(
                    name="🔍 Keyword Optimization",
                    value='\n'.join([f"• {k}" for k in analysis.keyword_optimization[:3]]),
                    inline=False
                )
            
            embed.set_footer(text="Focus on top suggestions for maximum impact")
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error in resume_review: {e}")
            await ctx.send("❌ Sorry, I encountered an error analyzing your resume. Please try again.")
    
    @bot.command(name='job_match')
    async def job_match(ctx, *, preferences: str):
        """Find job opportunities matching user preferences."""
        try:
            # Parse preferences
            pref_list = [pref.strip() for pref in preferences.split(',')]
            job_prefs = {
                'location': [],
                'industry': [],
                'salary_range': '',
                'remote_ok': False
            }
            
            # Simple parsing of preferences
            for pref in pref_list:
                pref_lower = pref.lower()
                if 'remote' in pref_lower:
                    job_prefs['remote_ok'] = True
                elif '$' in pref or 'k' in pref_lower:
                    job_prefs['salary_range'] = pref
                elif any(tech in pref_lower for tech in ['tech', 'software', 'finance', 'marketing']):
                    job_prefs['industry'].append(pref)
                else:
                    job_prefs['location'].append(pref)
            
            async with ctx.typing():
                # Create basic user profile (could be enhanced with stored profiles)
                user_profile = UserProfile(
                    skills=["General"],  # Placeholder - would use stored profile in real app
                    experience=[],
                    interests=[],
                    education=[]
                )
                
                # Get job matches
                matches = await bot.career_agent.match_jobs(user_profile, job_prefs)
            
            # Format response
            embed = discord.Embed(
                title="🎯 Job Matches",
                description=f"Based on preferences: {preferences}",
                color=0x0099ff
            )
            
            for i, match in enumerate(matches[:4], 1):
                field_value = (
                    f"**Fit Score:** {match.get('match_percentage', 85):.0f}%\n"
                    f"**Company:** {match.get('company_type', 'Various')}\n"
                    f"**Salary:** {match.get('salary_range', 'Competitive')}\n"
                    f"**Location:** {match.get('location', 'Multiple locations')}"
                )
                embed.add_field(
                    name=f"{i}. {match.get('job_title', 'Position Available')}",
                    value=field_value,
                    inline=True
                )
            
            embed.set_footer(text="Use !career_analyze with your skills for more personalized matches")
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error in job_match: {e}")
            await ctx.send("❌ Sorry, I encountered an error finding job matches. Please try again.")
    
    @bot.command(name='mock_interview')
    async def mock_interview(ctx, *, role: str):
        """Start a mock interview for the specified role."""
        try:
            # Validate role
            validation_result = InputValidator.validate_target_role(role)
            if not validation_result.is_valid:
                error_msg = format_validation_errors(validation_result)
                await ctx.send(f"❌ Invalid role:\n```{error_msg}```")
                return
            
            async with ctx.typing():
                # Create interview session
                session = await bot.career_agent.conduct_mock_interview(role)
                
                # Store session for user
                bot.interview_sessions[ctx.author.id] = session
            
            # Send first question
            embed = discord.Embed(
                title=f"🎤 Mock Interview: {role}",
                description="I'll ask you interview questions. Respond naturally and I'll provide feedback at the end.",
                color=0x9932cc
            )
            
            questions = session['questions'][:5]  # Limit to 5 questions
            
            embed.add_field(
                name="Question 1",
                value=questions[0],
                inline=False
            )
            
            embed.add_field(
                name="Instructions",
                value="• Answer each question thoroughly\n• Type your responses in chat\n• Use !interview_next for the next question\n• Use !interview_end to finish and get feedback",
                inline=False
            )
            
            embed.set_footer(text=f"Question 1 of {len(questions)}")
            await ctx.send(embed=embed)
            
            # Update session with current question
            bot.interview_sessions[ctx.author.id]['current_question'] = 0
            bot.interview_sessions[ctx.author.id]['answers'] = []
            bot.interview_sessions[ctx.author.id]['questions'] = questions
            
        except Exception as e:
            bot.logger.error(f"Error in mock_interview: {e}")
            await ctx.send("❌ Sorry, I encountered an error starting the mock interview. Please try again.")
    
    @bot.command(name='interview_next')
    async def interview_next(ctx, *, answer: Optional[str] = None):
        """Move to the next interview question."""
        try:
            user_id = ctx.author.id
            
            if user_id not in bot.interview_sessions:
                await ctx.send("❌ No active interview session. Start one with `!mock_interview <role>`")
                return
            
            session = bot.interview_sessions[user_id]
            current_q = session.get('current_question', 0)
            
            # Store the answer if provided
            if answer:
                session['answers'].append(answer)
            else:
                await ctx.send("❌ Please provide your answer: `!interview_next <your answer>`")
                return
            
            # Check if there are more questions
            questions = session['questions']
            if current_q + 1 >= len(questions):
                await ctx.send("🎉 Interview complete! Use `!interview_end` to get your feedback.")
                return
            
            # Move to next question
            next_q = current_q + 1
            session['current_question'] = next_q
            
            embed = discord.Embed(
                title=f"🎤 Mock Interview: {session['role']}",
                color=0x9932cc
            )
            
            embed.add_field(
                name=f"Question {next_q + 1}",
                value=questions[next_q],
                inline=False
            )
            
            embed.set_footer(text=f"Question {next_q + 1} of {len(questions)}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error in interview_next: {e}")
            await ctx.send("❌ Sorry, I encountered an error. Please try again.")
    
    @bot.command(name='interview_end')
    async def interview_end(ctx):
        """End the interview and get feedback."""
        try:
            user_id = ctx.author.id
            
            if user_id not in bot.interview_sessions:
                await ctx.send("❌ No active interview session found.")
                return
            
            session = bot.interview_sessions[user_id]
            answers = session.get('answers', [])
            
            if not answers:
                await ctx.send("❌ No answers recorded. Please answer at least one question.")
                return
            
            async with ctx.typing():
                # Get interview feedback
                feedback = await bot.career_agent.evaluate_interview_answers(
                    session['session_id'], 
                    answers
                )
            
            # Format feedback
            embed = discord.Embed(
                title="📊 Interview Feedback",
                description=f"Performance Analysis for {session['role']}",
                color=0x00ff00 if feedback.overall_performance >= 80 else 0xffaa00 if feedback.overall_performance >= 60 else 0xff0000
            )
            
            # Performance scores
            scores_text = (
                f"**Overall:** {feedback.overall_performance:.0f}/100\n"
                f"**Communication:** {feedback.communication_skills:.0f}/100\n"
                f"**Technical:** {feedback.technical_knowledge:.0f}/100\n"
                f"**Problem Solving:** {feedback.problem_solving:.0f}/100"
            )
            embed.add_field(name="📈 Performance Scores", value=scores_text, inline=False)
            
            # Areas for improvement
            if feedback.areas_for_improvement:
                embed.add_field(
                    name="🔧 Areas for Improvement",
                    value='\n'.join([f"• {area}" for area in feedback.areas_for_improvement[:3]]),
                    inline=False
                )
            
            # Practice suggestions
            if feedback.suggested_practice_topics:
                embed.add_field(
                    name="📚 Practice Topics",
                    value='\n'.join([f"• {topic}" for topic in feedback.suggested_practice_topics[:3]]),
                    inline=False
                )
            
            embed.set_footer(text="Keep practicing to improve your interview skills!")
            await ctx.send(embed=embed)
            
            # Clean up session
            del bot.interview_sessions[user_id]
            
        except Exception as e:
            bot.logger.error(f"Error in interview_end: {e}")
            await ctx.send("❌ Sorry, I encountered an error processing your feedback. Please try again.")
    
    @bot.command(name='skill_gap')
    async def skill_gap(ctx, *, input_text: str):
        """Analyze skill gaps for a target role."""
        try:
            # Parse input - expect format: "current skills | target role"
            if ' | ' not in input_text:
                await ctx.send("❌ Please use format: `!skill_gap <current skills> | <target role>`\nExample: `!skill_gap Python, SQL | Data Scientist`")
                return
            
            skills_part, role_part = input_text.split(' | ', 1)
            
            current_skills = [skill.strip() for skill in skills_part.split(',')]
            target_role = role_part.strip()
            
            # Validate inputs
            skills_validation = InputValidator.validate_skills_list(current_skills)
            role_validation = InputValidator.validate_target_role(target_role)
            
            if not skills_validation.is_valid or not role_validation.is_valid:
                errors = []
                if not skills_validation.is_valid:
                    errors.extend(skills_validation.errors)
                if not role_validation.is_valid:
                    errors.extend(role_validation.errors)
                await ctx.send(f"❌ Validation errors:\n```{chr(10).join(errors)}```")
                return
            
            async with ctx.typing():
                # Analyze skill gap
                analysis = await bot.career_agent.analyze_skill_gap(current_skills, target_role)
            
            # Format response
            embed = discord.Embed(
                title=f"🎯 Skill Gap Analysis: {target_role}",
                description=f"Current skills: {', '.join(current_skills[:5])}",
                color=0xff6600
            )
            
            # Relevant skills
            if analysis.get('relevant_skills'):
                embed.add_field(
                    name="✅ Skills You Have",
                    value='\n'.join([f"• {skill}" for skill in analysis['relevant_skills'][:4]]),
                    inline=True
                )
            
            # Missing skills
            if analysis.get('missing_skills'):
                embed.add_field(
                    name="📚 Skills to Develop",
                    value='\n'.join([f"• {skill}" for skill in analysis['missing_skills'][:4]]),
                    inline=True
                )
            
            # Learning path
            if analysis.get('learning_path'):
                embed.add_field(
                    name="🗺️ Learning Path",
                    value='\n'.join([f"{i+1}. {step}" for i, step in enumerate(analysis['learning_path'][:3])]),
                    inline=False
                )
            
            # Timeline
            timeline = analysis.get('timeline', '3-6 months')
            embed.add_field(
                name="⏱️ Estimated Timeline",
                value=timeline,
                inline=True
            )
            
            embed.set_footer(text="Focus on high-priority skills first for faster career transition")
            await ctx.send(embed=embed)
            
        except Exception as e:
            bot.logger.error(f"Error in skill_gap: {e}")
            await ctx.send("❌ Sorry, I encountered an error analyzing skill gaps. Please try again.")
    
    @bot.command(name='profile_create')
    async def profile_create(ctx):
        """Help user create a career profile (placeholder for future feature)."""
        embed = discord.Embed(
            title="👤 Career Profile Creation",
            description="This feature is coming soon! For now, you can:",
            color=0x0099ff
        )
        
        embed.add_field(
            name="Current Options",
            value=(
                "• Use `!career_analyze <skills>` for quick analysis\n"
                "• Use `!skill_gap <skills> | <role>` for specific guidance\n"
                "• Upload resume with `!resume_review` for detailed feedback"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Coming Soon",
            value=(
                "• Persistent user profiles\n"
                "• Career goal tracking\n"
                "• Progress monitoring\n"
                "• Personalized recommendations"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    return bot


async def main():
    """Main function to run the Discord bot."""
    try:
        # Load configuration
        config = Config()
        
        # Create and start bot
        bot = create_bot(config)
        
        print("🤖 Starting Career Coach Discord Bot...")
        print(f"📊 LLM Provider: {config.llm_provider}")
        print(f"📝 Log Level: {config.log_level}")
        print("=" * 50)
        
        # Run the bot
        await bot.start(config.discord_bot_token)
        
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown requested")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logging.error(f"Bot startup error: {e}")
    finally:
        print("🔄 Cleaning up...")


if __name__ == "__main__":
    asyncio.run(main())
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
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

import discord
from discord.ext import commands

from config import Config
from career_agent import CareerAgent, UserProfile, AnalysisType
from utils.logger import setup_logger
from utils.validators import (
    InputValidator, validate_discord_message_length, 
    format_validation_errors
)
from storage import BotStorage


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
            command_prefix='!',  # Keep prefix for backward compatibility
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
        
        self.config = config
        self.career_agent = CareerAgent(config)
        self.logger = setup_logger(__name__, config.log_level)
        
        # Initialize storage system
        self.storage = BotStorage(data_dir="data", log_level=config.log_level)
        
        # Load persistent data
        self.user_contexts = self.storage.load_user_contexts()
        self.interview_sessions = self.storage.load_interview_sessions()
        
        # Initialize conversation handler
        from conversation_handler import ConversationHandler
        self.conversation_handler = ConversationHandler()
        
        loaded_users = len(self.user_contexts)
        loaded_sessions = len(self.interview_sessions) 
        self.logger.info(f"Career Coach Discord Bot initialized - Loaded {loaded_users} users, {loaded_sessions} interview sessions")
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        self.logger.info(f'Bot is ready! Logged in as {self.user.name} (ID: {self.user.id})')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="Chat with me about your career!"
        )
        await self.change_presence(activity=activity)

    def _is_greeting(self, message: str) -> bool:
        """Check if a message is a greeting."""
        greetings = {'hi', 'hello', 'hey', 'halo', 'hai'}
        return message.lower().strip() in greetings
    
    def _format_conversation_response(self, response_text: str) -> Union[str, discord.Embed]:
        """Format the response appropriately based on content."""
        # For very short responses, just return as text
        if len(response_text) < 100 and not any(marker in response_text.lower() for marker in ['steps:', 'recommendations:', '1.', '•']):
            return response_text

        try:
            # Check if response has structured data
            if any(marker in response_text.lower() for marker in ['steps:', 'recommendations:', '1.', '•', '\n\n']):
                embed = discord.Embed(color=0x00ff00)
                
                # Split response into sections
                sections = response_text.split('\n\n')
                
                # First section as main description
                embed.description = sections[0]
                
                # Process remaining sections
                for section in sections[1:]:
                    if ':' in section:
                        title, content = section.split(':', 1)
                        # Clean up the title and add appropriate emoji
                        clean_title = title.strip()
                        if 'step' in clean_title.lower():
                            emoji = '📝'
                        elif 'recommend' in clean_title.lower():
                            emoji = '💡'
                        elif 'suggest' in clean_title.lower():
                            emoji = '✨'
                        elif 'example' in clean_title.lower():
                            emoji = '🔍'
                        else:
                            emoji = '💬'
                        
                        embed.add_field(
                            name=f"{emoji} {clean_title}",
                            value=content.strip(),
                            inline=False
                        )
                    else:
                        # Add as a continuation if it's not a new section
                        last_field = embed.fields[-1] if embed.fields else None
                        if last_field:
                            updated_value = last_field.value + "\n\n" + section.strip()
                            # Remove and re-add field to update it
                            embed.remove_field(-1)
                            embed.add_field(
                                name=last_field.name,
                                value=updated_value,
                                inline=False
                            )
                        else:
                            embed.add_field(
                                name="� Additional Info",
                                value=section.strip(),
                                inline=False
                            )
                
                return embed
            else:
                # For conversational responses, just return as text
                return response_text
                
        except Exception as e:
            # If any error in formatting, fall back to plain text
            self.logger.error(f"Error formatting response: {e}")
            return response_text
    
    async def _generate_contextual_response(self, message: discord.Message, context: Dict[str, Any]) -> Union[str, discord.Embed]:
        """Generate a contextual response based on the conversation history."""
        try:
            # Get response from career agent
            response = await self.career_agent.generate_chat_response(
                message.content,
                context
            )
            
            # Extract any skills mentioned
            skills = self.conversation_handler.extract_skills(message.content)
            if skills:
                # Update context with skills
                context['skills'] = context.get('skills', []) + skills
            
            # Format the response appropriately
            return self._format_conversation_response(response)
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble right now. Could you try rephrasing your question?"
    
    async def on_message(self, message):
        """Handle all messages sent in the server."""
        # Ignore messages from self
        if message.author == self.user:
            return
            
        # First, process commands for backward compatibility
        await self.process_commands(message)
        
        # If message starts with prefix, don't process it as conversation
        if message.content.startswith(self.command_prefix):
            return
            
        try:
            # Get user context
            user_context = self.user_contexts.get(message.author.id, {})
            
            # Get or create user context
            if message.author.id not in self.user_contexts:
                self.user_contexts[message.author.id] = {
                    'state': 'initial',
                    'conversation_history': []
                }
            
            user_context = self.user_contexts[message.author.id]
            user_context['conversation_history'].append({
                'user': message.content,
                'timestamp': message.created_at.isoformat()
            })
            
            # Auto-save user contexts every 10 messages
            history_length = len(user_context.get('conversation_history', []))
            if history_length % 10 == 0:
                self._auto_save_data()

            # Handle the message based on content and context
            async with message.channel.typing():
                if self._is_greeting(message.content) and user_context['state'] == 'initial':
                    response = self.conversation_handler.get_response_for_greeting()
                    user_context['state'] = 'engaged'
                else:
                    # Try to understand user's message and provide relevant response
                    response = await self._generate_contextual_response(message, user_context)
                
                # Update conversation history with bot's response
                response_text = response if isinstance(response, str) else str(response)
                user_context['conversation_history'].append({
                    'bot': response_text,
                    'timestamp': datetime.now().isoformat()
                })
                
                # If response is a string, send directly
                if isinstance(response, str):
                    await message.channel.send(response)
                # If response is an embed, send as embed
                elif isinstance(response, discord.Embed):
                    await message.channel.send(embed=response)
                # If response is a list/tuple of embeds, send all
                elif isinstance(response, (list, tuple)):
                    for item in response:
                        if isinstance(item, discord.Embed):
                            await message.channel.send(embed=item)
                        else:
                            await message.channel.send(item)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            await message.channel.send(
                "I encountered an error processing your message. "
                "Please try rephrasing or use one of the specific commands like !help"
            )
    
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
    
    def _auto_save_data(self):
        """Auto-save user data periodically."""
        try:
            self.storage.save_user_contexts(self.user_contexts)
            self.storage.save_interview_sessions(self.interview_sessions)
            self.logger.debug("Auto-saved user data")
        except Exception as e:
            self.logger.error(f"Failed to auto-save data: {e}")
    
    async def save_all_data(self):
        """Save all bot data before shutdown."""
        try:
            self.logger.info("Saving all bot data before shutdown...")
            contexts_saved = self.storage.save_user_contexts(self.user_contexts)
            sessions_saved = self.storage.save_interview_sessions(self.interview_sessions)
            
            if contexts_saved and sessions_saved:
                self.logger.info("✅ All data saved successfully")
            else:
                self.logger.warning("⚠️ Some data may not have been saved properly")
                
        except Exception as e:
            self.logger.error(f"Error saving data on shutdown: {e}")
    
    async def close(self):
        """Override close to save data before shutting down."""
        await self.save_all_data()
        await super().close()


# Create bot instance
def create_bot(config: Config) -> CareerCoachBot:
    """Create and configure the Discord bot."""
    bot = CareerCoachBot(config)
    
    @bot.command(name='help')
    async def help_command(ctx):
        """Show available commands and usage information."""
        embed = discord.Embed(
            title="🤖 Career Coach Bot",
            description="I'm your AI career coach! You can chat with me naturally or use commands.",
            color=0x00ff00
        )
        
        # Natural conversation examples
        conversation_examples = [
            ("💬 Chat with me naturally", 
             "Just talk to me like you would to a career coach! Examples:\n"
             "• 'Can you help me with my career?'\n"
             "• 'I want to become a Data Scientist'\n"
             "• 'Review my resume please'\n"
             "• 'What jobs match my skills?'"
            ),
        ]
        
        # Traditional commands (for backward compatibility)
        commands_info = [
            ("⌨️ Or use traditional commands:", "The following commands are also available:"),
            ("!career_analyze <skills>", "Analyze career paths\n*Example: !career_analyze Python, Machine Learning*"),
            ("!resume_review", "Review resume (attach .txt file)"),
            ("!job_match <preferences>", "Find job matches\n*Example: !job_match Remote, Tech*"),
            ("!mock_interview <role>", "Practice interviews\n*Example: !mock_interview Software Engineer*"),
            ("!skill_gap <skills | role>", "Analyze skill gaps\n*Example: !skill_gap Python | Data Scientist*")
        ]
        
        # Add conversation examples
        for name, description in conversation_examples:
            embed.add_field(name=name, value=description, inline=False)
            
        # Add command information
        for name, description in commands_info:
            embed.add_field(name=name, value=description, inline=False)
        
        embed.add_field(
            name="💡 Tips",
            value="• Be specific about your skills and goals\n"
                 "• Attach resume as .txt file for review\n"
                 "• Feel free to ask follow-up questions",
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
            
            # Save interview sessions
            bot.storage.save_interview_sessions(bot.interview_sessions)            # Send first question
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
            
            # Save updated interview sessions
            bot.storage.save_interview_sessions(bot.interview_sessions)
            
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
    bot = None
    try:
        # Load configuration
        config = Config()
        
        # Create and start bot
        bot = create_bot(config)
        
        print("🤖 Starting Career Coach Discord Bot...")
        print(f"📊 LLM Provider: {config.llm_provider}")
        print(f"📝 Log Level: {config.log_level}")
        
        # Show storage info
        stats = bot.storage.get_storage_stats()
        print(f"💾 Data directory: {stats['data_directory']}")
        print(f"💾 Loaded {len(bot.user_contexts)} user contexts")
        print("=" * 50)
        
        # Run the bot
        await bot.start(config.discord_bot_token)
        
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown requested by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logging.error(f"Bot startup error: {e}")
    finally:
        print("🔄 Cleaning up...")
        if bot:
            try:
                await bot.save_all_data()
                print("✅ Data saved successfully")
            except Exception as e:
                print(f"⚠️ Error saving data: {e}")
        print("👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
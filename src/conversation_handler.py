"""
Conversation handler for the Career Coach chatbot.

Handles natural language processing and conversation management
for more human-like interactions.
"""

import re
from typing import Optional, Tuple, List

class ConversationHandler:
    """
    Handles natural language processing and conversation flow for the chatbot.
    Determines intent and extracts relevant information from user messages.
    """
    
    def __init__(self):
        """Initialize conversation handler with intent patterns."""
        self.intent_patterns = {
            'career_analysis': [
                r'(?i)what career|career path|job opportunities|career advice',
                r'(?i)my skills? (?:is|are|include)',
                r'(?i)recommend.*career|suggest.*career'
            ],
            'resume_review': [
                r'(?i)review.*resume|check.*resume',
                r'(?i)improve.*resume|resume.*feedback',
                r'(?i)cv.*review|review.*cv'
            ],
            'job_match': [
                r'(?i)find.*job|job.*match',
                r'(?i)looking for.*job|job.*opportunities',
                r'(?i)job.*search|search.*job'
            ],
            'mock_interview': [
                r'(?i)interview.*practice|practice.*interview',
                r'(?i)mock.*interview|prepare.*interview',
                r'(?i)interview.*question'
            ],
            'skill_gap': [
                r'(?i)skill.*gap|missing.*skills',
                r'(?i)learn.*skills|improve.*skills',
                r'(?i)what.*skills.*need'
            ],
            'greeting': [
                r'(?i)^hi$|^hello$|^hey$',
                r'(?i)^good\s*(morning|afternoon|evening)',
                r'(?i)help me|assist me|can you help'
            ]
        }
    
    def detect_intent(self, message: str) -> Tuple[Optional[str], float]:
        """
        Detect the user's intent from their message.
        
        Args:
            message: The user's message text
            
        Returns:
            Tuple of (intent_name, confidence_score)
        """
        max_confidence = 0
        detected_intent = None
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, message)
                if matches:
                    # Calculate confidence based on match length and position
                    confidence = len(max(matches, key=len)) / len(message)
                    if confidence > max_confidence:
                        max_confidence = confidence
                        detected_intent = intent
        
        return detected_intent, max_confidence
    
    def extract_skills(self, message: str) -> List[str]:
        """Extract skills from a message."""
        # Look for skills after phrases like "I know" or "I'm good at"
        skill_patterns = [
            r'(?i)(?:I know|I\'m good at|my skills are|I can|I have experience (?:in|with))\s+([\w\s,]+)',
            r'(?i)experience (?:in|with)\s+([\w\s,]+)',
            r'(?i)skilled (?:in|with)\s+([\w\s,]+)'
        ]
        
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, message)
            if matches:
                # Split skills by comma or 'and'
                for match in matches:
                    skills.extend([s.strip() for s in re.split(r',|\sand\s', match) if s.strip()])
        
        return list(set(skills))
    
    def extract_role(self, message: str) -> Optional[str]:
        """Extract target role from a message."""
        role_patterns = [
            r'(?i)(?:want to be|become|work as|position as|role of|job as) (?:an? )?(\w+\s*\w*) ?(?:position|role)?',
            r'(?i)interested in (?:becoming|being) (?:an? )?(\w+\s*\w*)',
            r'(?i)looking for (\w+\s*\w*) (?:position|role|job)'
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_response_for_greeting(self) -> str:
        """Get appropriate response for greeting."""
        return (
            "👋 Hi! I'm your AI Career Coach. I can help you with:\n\n"
            "• Career path analysis and recommendations\n"
            "• Resume review and improvement suggestions\n"
            "• Job matching based on your preferences\n"
            "• Mock interview practice\n"
            "• Skill gap analysis\n\n"
            "Just tell me what you'd like help with! For example, you can say 'I want career advice' or 'Can you review my resume?'"
        )
    
    def get_clarifying_questions(self, intent: str) -> str:
        """Get clarifying questions based on detected intent."""
        questions = {
            'career_analysis': (
                "I can help analyze career paths! To give you better recommendations, "
                "could you tell me about your skills and experience? For example: "
                "'I know Python, SQL, and have 2 years of data analysis experience'"
            ),
            'resume_review': (
                "I'd be happy to review your resume! Just send it as a text file and "
                "I'll analyze it for you. If you're targeting a specific role, let me know!"
            ),
            'job_match': (
                "I can help find job matches! What are your preferences in terms of:\n"
                "• Location (remote/specific city)\n"
                "• Industry\n"
                "• Salary expectations\n"
                "Just share what's important to you!"
            ),
            'mock_interview': (
                "Let's practice interviewing! What role would you like to prepare for? "
                "For example: 'Software Engineer' or 'Data Scientist'"
            ),
            'skill_gap': (
                "I can help identify skills to develop! Could you tell me:\n"
                "1. Your current skills\n"
                "2. The role you're targeting\n"
                "For example: 'I know Python and SQL, and want to become a Data Scientist'"
            )
        }
        
        return questions.get(intent, "Could you please be more specific about what you're looking for?")
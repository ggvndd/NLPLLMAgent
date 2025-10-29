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
                r'(?i)my skills? (?:is|are|include)|skills.*in|have.*skills',
                r'(?i)recommend.*career|suggest.*career|python.*skills',
                r'(?i)machine.*learning|what.*can.*i.*do|skills.*available'
            ],
            'resume_review': [
                r'(?i)review.*resume|check.*resume',
                r'(?i)improve.*resume|resume.*feedback',
                r'(?i)cv.*review|review.*cv'
            ],
            'job_match': [
                r'(?i)find.*job|job.*search|looking.*for.*job',
                r'(?i)career.*opportunit|job.*match|work.*opportunit',
                r'(?i)employment.*opportunit|job.*recommendation|career.*move',
                r'(?i)remote.*work|data science.*job|software.*job',
                r'(?i)engineering.*job|find.*work|job.*opening'
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
            ],
            'casual_chat': [
                r'(?i)how.*you|how.*going|what.*up',
                r'(?i)weather|tired|stressed|busy|bored',
                r'(?i)thanks|thank you|appreciate',
                r'(?i)funny|lol|haha|joke',
                r'(?i)weekend|holiday|vacation',
                r'(?i)food|coffee|lunch|dinner',
                r'(?i)music|movie|tv|netflix',
                r'(?i)^nice$|^cool$|^awesome$|^great$'
            ],
            'personal_check': [
                r'(?i)how.*day|how.*weekend|how.*feeling',
                r'(?i)what.*doing|keeping busy',
                r'(?i)everything.*ok|you.*alright'
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
            r'(?i)(?:have skills? (?:in|with)|skills? (?:in|include))\s+([\w\s,.-]+?)(?:\.|and I|I have|\s*\d|\s*with)',
            r'(?i)experience (?:in|with)\s+([\w\s,]+)',
            r'(?i)skilled (?:in|with)\s+([\w\s,]+)',
            r'(?i)proficient (?:in|with)\s+([\w\s,]+)'
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
    
    def extract_experience(self, message: str) -> List[str]:
        """Extract experience information from a message."""
        experience_patterns = [
            r'(?i)(\d+\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|work|working)(?:\s*(?:as|in|with))?[^.]*)',
            r'(?i)((?:worked|working|experience)\s*(?:as|in|at|with)[^.]*)',
            r'(?i)(internship[^.]*)',
            r'(?i)(freelance[^.]*)',
            r'(?i)(recent graduate|new graduate|just graduated)'
        ]
        
        experience = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                experience.append(match.strip())
        
        return experience if experience else []
    
    def extract_interests(self, message: str) -> List[str]:
        """Extract interests and career goals from a message."""
        interest_patterns = [
            r'(?i)interested in\s+([\w\s,]+?)(?:\.|,|$)',
            r'(?i)love\s+([\w\s,]+?)(?:\.|,|$)',
            r'(?i)passionate about\s+([\w\s,]+?)(?:\.|,|$)',
            r'(?i)enjoy\s+([\w\s,]+?)(?:\.|,|$)',
            r'(?i)want to work (?:in|with)\s+([\w\s,]+?)(?:\.|,|$)'
        ]
        
        interests = []
        for pattern in interest_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                # Split by comma or 'and'
                interests.extend([i.strip() for i in re.split(r',|\sand\s', match) if i.strip()])
        
        return interests if interests else []
    
    def extract_education(self, message: str) -> List[str]:
        """Extract education information from a message."""
        education_patterns = [
            r'(?i)(bachelor\'?s?\s*(?:degree\s*)?(?:in\s*)?[\w\s]*)',
            r'(?i)(master\'?s?\s*(?:degree\s*)?(?:in\s*)?[\w\s]*)',
            r'(?i)(phd|doctorate\s*(?:in\s*)?[\w\s]*)',
            r'(?i)(degree\s*in\s*[\w\s]*)',
            r'(?i)(graduated\s*(?:from\s*)?[\w\s]*)',
            r'(?i)(university\s*[\w\s]*)',
            r'(?i)(college\s*[\w\s]*)',
            r'(?i)(certification\s*in\s*[\w\s]*)',
            r'(?i)(online courses?\s*in\s*[\w\s]*)'
        ]
        
        education = []
        for pattern in education_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                education.append(match.strip())
        
        return education if education else []
    
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
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import re


class Skill(ABC):
    """
    Base class for all skills
    """
    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        self.enabled = True
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill with given context"""
        pass
    
    def can_handle(self, query: str) -> bool:
        """Check if this skill can handle the query"""
        return False


class KnowledgeSearchSkill(Skill):
    """Skill for searching knowledge base"""
    
    def __init__(self, kb_service):
        super().__init__(
            name="חיפוש ידע",
            description="חיפוש מידע במאגר הידע המקצועי",
            category="search"
        )
        self.kb_service = kb_service
    
    def can_handle(self, query: str) -> bool:
        keywords = ['איך', 'מה זה', 'הסבר', 'למד', 'מידע', 'תיעוד']
        return any(keyword in query for keyword in keywords)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        query = context.get('query', '')
        results = await self.kb_service.search(query, limit=5)
        
        return {
            'skill_used': self.name,
            'results': results,
            'context': await self.kb_service.get_context_for_query(query)
        }


class ReservationSkill(Skill):
    """Skill for handling reservation queries"""
    
    def __init__(self):
        super().__init__(
            name="ניהול הזמנות",
            description="עזרה בניהול והזמנת חדרים",
            category="reservations"
        )
    
    def can_handle(self, query: str) -> bool:
        keywords = ['הזמנה', 'חדר', 'הזמן', 'book', 'reservation', 'check-in', 'check-out']
        return any(keyword in query.lower() for keyword in keywords)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        query = context.get('query', '')
        
        # Extract reservation intent
        intent = 'general'
        if 'חדש' in query or 'צור' in query:
            intent = 'create'
        elif 'עדכן' in query or 'שנה' in query:
            intent = 'update'
        elif 'מחק' in query or 'בטל' in query:
            intent = 'cancel'
        
        return {
            'skill_used': self.name,
            'intent': intent,
            'category': self.category,
            'guidance': self._get_guidance(intent)
        }
    
    def _get_guidance(self, intent: str) -> str:
        guidance_map = {
            'create': 'ליצירת הזמנה חדשה: תפריט הזמנות > הזמנה חדשה > בחר תאריכים וחדר',
            'update': 'לעדכון הזמנה: תפריט הזמנות > חפש הזמנה > ערוך',
            'cancel': 'לביטול הזמנה: תפריט הזמנות > חפש הזמנה > בטל הזמנה',
            'general': 'מערכת ההזמנות מאפשרת ניהול מלא של הזמנות החדרים'
        }
        return guidance_map.get(intent, guidance_map['general'])


class ReportGenerationSkill(Skill):
    """Skill for generating reports"""
    
    def __init__(self):
        super().__init__(
            name="יצירת דוחות",
            description="הפקת דוחות ואנליטיקה",
            category="reports"
        )
    
    def can_handle(self, query: str) -> bool:
        keywords = ['דוח', 'report', 'תפוסה', 'הכנסות', 'סטטיסטיקה', 'נתונים']
        return any(keyword in query.lower() for keyword in keywords)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        query = context.get('query', '')
        
        # Determine report type
        report_type = 'general'
        if 'תפוסה' in query:
            report_type = 'occupancy'
        elif 'הכנסות' in query or 'כספי' in query:
            report_type = 'revenue'
        elif 'תשלומים' in query:
            report_type = 'payments'
        
        return {
            'skill_used': self.name,
            'report_type': report_type,
            'category': self.category,
            'instructions': self._get_instructions(report_type)
        }
    
    def _get_instructions(self, report_type: str) -> str:
        instructions_map = {
            'occupancy': 'דוח תפוסה: תפריט דוחות > תפוסה > בחר תאריך > הפק דוח',
            'revenue': 'דוח הכנסות: תפריט דוחות > הכנסות > בחר תקופה > ייצא',
            'payments': 'דוח תשלומים: תפריט דוחות > תשלומים > סנן לפי סטטוס',
            'general': 'מערכת הדוחות: תפריט דוחות > בחר סוג דוח > הגדר פרמטרים'
        }
        return instructions_map.get(report_type, instructions_map['general'])


class TroubleshootingSkill(Skill):
    """Skill for troubleshooting technical issues"""
    
    def __init__(self):
        super().__init__(
            name="פתרון בעיות",
            description="תמיכה טכנית ופתרון תקלות",
            category="troubleshooting"
        )
    
    def can_handle(self, query: str) -> bool:
        keywords = ['בעיה', 'שגיאה', 'תקלה', 'לא עובד', 'error', 'bug', 'תקוע', 'איטי']
        return any(keyword in query.lower() for keyword in keywords)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        query = context.get('query', '').lower()
        
        # Identify issue type
        issue_type = 'general'
        if 'איטי' in query or 'slow' in query:
            issue_type = 'performance'
        elif 'הדפס' in query or 'print' in query:
            issue_type = 'printing'
        elif 'חיבור' in query or 'connection' in query:
            issue_type = 'connectivity'
        elif 'התחבר' in query or 'login' in query:
            issue_type = 'login'
        
        return {
            'skill_used': self.name,
            'issue_type': issue_type,
            'category': self.category,
            'solution': self._get_solution(issue_type),
            'priority': self._get_priority(issue_type)
        }
    
    def _get_solution(self, issue_type: str) -> str:
        solutions = {
            'performance': '1. נקה cache של הדפדפן\n2. סגור טאבים מיותרים\n3. רענן את הדף',
            'printing': '1. בדוק חיבור למדפסת\n2. ודא שיש נייר וטונר\n3. נסה להדפיס דף בדיקה',
            'connectivity': '1. בדוק חיבור לאינטרנט\n2. נסה לרענן את הדף\n3. צור קשר עם IT',
            'login': '1. בדוק שם משתמש וסיסמה\n2. נסה "שכחתי סיסמה"\n3. צור קשר עם מנהל',
            'general': 'אנא תאר את הבעיה ביתר פירוט כדי שאוכל לעזור טוב יותר'
        }
        return solutions.get(issue_type, solutions['general'])
    
    def _get_priority(self, issue_type: str) -> str:
        if issue_type in ['connectivity', 'login']:
            return 'high'
        return 'medium'


class LanguageProcessingSkill(Skill):
    """Skill for advanced language understanding"""
    
    def __init__(self):
        super().__init__(
            name="עיבוד שפה",
            description="הבנה וניתוח של שפה טבעית",
            category="language"
        )
    
    def can_handle(self, query: str) -> bool:
        # This skill is always active for language processing
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        query = context.get('query', '')
        
        # Extract entities (simple implementation)
        entities = {
            'dates': self._extract_dates(query),
            'numbers': self._extract_numbers(query),
            'actions': self._extract_actions(query)
        }
        
        # Determine sentiment
        sentiment = self._analyze_sentiment(query)
        
        return {
            'skill_used': self.name,
            'entities': entities,
            'sentiment': sentiment,
            'language': 'hebrew',
            'category': self.category
        }
    
    def _extract_dates(self, text: str) -> List[str]:
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}\.\d{1,2}\.\d{4}',
            r'היום|מחר|אתמול'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        return dates
    
    def _extract_numbers(self, text: str) -> List[str]:
        return re.findall(r'\d+', text)
    
    def _extract_actions(self, text: str) -> List[str]:
        action_words = ['צור', 'מחק', 'עדכן', 'הצג', 'חפש', 'הדפס', 'ייצא']
        return [word for word in action_words if word in text]
    
    def _analyze_sentiment(self, text: str) -> str:
        positive_words = ['תודה', 'מצוין', 'נהדר', 'עזר']
        negative_words = ['בעיה', 'שגיאה', 'לא עובד', 'תקלה']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'


class SkillsManager:
    """
    Manager for all skills - coordinates skill execution
    """
    
    def __init__(self, kb_service=None):
        self.skills: List[Skill] = []
        self.kb_service = kb_service
        self._initialize_skills()
    
    def _initialize_skills(self):
        """Initialize all available skills"""
        if self.kb_service:
            self.skills.append(KnowledgeSearchSkill(self.kb_service))
        
        self.skills.extend([
            ReservationSkill(),
            ReportGenerationSkill(),
            TroubleshootingSkill(),
            LanguageProcessingSkill()
        ])
    
    def get_available_skills(self) -> List[Dict[str, str]]:
        """Get list of all available skills"""
        return [
            {
                'name': skill.name,
                'description': skill.description,
                'category': skill.category,
                'enabled': skill.enabled
            }
            for skill in self.skills
        ]
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query and execute relevant skills
        """
        results = {
            'query': query,
            'skills_triggered': [],
            'data': {}
        }
        
        # Find relevant skills
        relevant_skills = [
            skill for skill in self.skills
            if skill.enabled and skill.can_handle(query)
        ]
        
        # Execute skills
        for skill in relevant_skills:
            try:
                skill_result = await skill.execute({'query': query})
                results['skills_triggered'].append(skill.name)
                results['data'][skill.category] = skill_result
            except Exception as e:
                print(f"Error executing skill {skill.name}: {e}")
        
        return results
    
    def enable_skill(self, skill_name: str):
        """Enable a specific skill"""
        for skill in self.skills:
            if skill.name == skill_name:
                skill.enabled = True
                return True
        return False
    
    def disable_skill(self, skill_name: str):
        """Disable a specific skill"""
        for skill in self.skills:
            if skill.name == skill_name:
                skill.enabled = False
                return True
        return False

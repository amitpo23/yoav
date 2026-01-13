import os
from openai import AsyncOpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """
    שירות לניהול תקשורת עם מודל השפה (OpenAI)
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        
        # הגדרת הקונטקסט של המערכת לתמיכה טכנית בבתי מלון
        self.system_prompt = """
        אתה עוזר AI לתמיכה טכנית במערכות ניהול לבתי מלון.
        
        תפקידך:
        1. לענות על שאלות טכניות בנוגע למערכות ניהול בתי מלון
        2. לעזור בפתרון בעיות ותקלות
        3. להדריך משתמשים בשימוש במערכת
        4. לספק מידע מדויק ומועיל
        
        הנחיות:
        - תמיד היה מקצועי ואדיב
        - תן תשובות ברורות ומפורטות
        - אם אתה לא בטוח במשהו, אמר זאת בבירור
        - השתמש במידע מ-Knowledge Base כשזמין
        - תן דוגמאות מעשיות כשרלוונטי
        - תמיד ענה בעברית אלא אם התבקש אחרת
        """
    
    def is_available(self) -> bool:
        """בדיקה אם השירות זמין"""
        return self.client is not None
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        context: str = None,
        temperature: float = 0.7
    ) -> str:
        """
        יצירת תשובה מהמודל
        
        Args:
            messages: רשימת הודעות בפורמט OpenAI
            context: קונטקסט נוסף מ-Knowledge Base
            temperature: רמת היצירתיות של התשובה
        
        Returns:
            התשובה מהמודל
        """
        if not self.is_available():
            return "מצטער, שירות ה-AI אינו זמין כרגע. אנא בדוק את הגדרות ה-API."
        
        # הוספת קונטקסט מ-Knowledge Base אם קיים
        system_message = self.system_prompt
        if context:
            system_message += f"\n\nמידע רלוונטי מבסיס הידע:\n{context}"
        
        # הכנת ההודעות
        full_messages = [
            {"role": "system", "content": system_message}
        ] + messages
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"שגיאה ביצירת תשובה: {str(e)}"
    
    async def summarize_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        סיכום שיחה
        """
        if not self.is_available():
            return ""
        
        summary_prompt = [
            {
                "role": "system",
                "content": "סכם את השיחה הבאה בצורה תמציתית וברורה:"
            },
            {
                "role": "user",
                "content": "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            }
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=summary_prompt,
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message.content
        except:
            return ""

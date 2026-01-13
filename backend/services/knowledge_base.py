import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class KnowledgeBaseService:
    """
    שירות לניהול מאגר הידע (Knowledge Base) - גרסה פשוטה בזיכרון
    """
    
    def __init__(self):
        self.db_path = os.getenv("KNOWLEDGE_DB_PATH", "./data/knowledge_db.json")
        self.items: List[Dict] = []
        
        # טעינת נתונים קיימים או אתחול
        self._load_from_file()
        
        # אתחול עם נתונים בסיסיים אם ריק
        if len(self.items) == 0:
            self._initialize_base_knowledge()
            self._save_to_file()
    
    def _load_from_file(self):
        """טעינת נתונים מקובץ"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
        except Exception:
            self.items = []
    
    def _save_to_file(self):
        """שמירת נתונים לקובץ"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def is_available(self) -> bool:
        """בדיקה אם השירות זמין"""
        return True
    
    def _initialize_base_knowledge(self):
        """אתחול מאגר הידע עם מידע בסיסי"""
        base_knowledge = [
            {
                "title": "התחברות למערכת",
                "content": "להתחברות למערכת יש להזין שם משתמש וסיסמה בדף הכניסה. במקרה של שכחת סיסמה, יש ללחוץ על 'שכחתי סיסמה' ולעקוב אחר ההוראות.",
                "category": "authentication",
                "tags": ["login", "password", "התחברות"]
            },
            {
                "title": "ניהול הזמנות",
                "content": "לניהול הזמנות, היכנס לתפריט 'הזמנות', בחר את התאריך והחדר הרצוי. ניתן להוסיף פרטי אורח, לבחור חבילות ושירותים נוספים. לאחר מילוי כל הפרטים, לחץ על 'שמור הזמנה'.",
                "category": "reservations",
                "tags": ["booking", "הזמנות", "חדרים"]
            },
            {
                "title": "דוחות ותשלומים",
                "content": "מערכת הדוחות מאפשרת ליצור דוחות על תפוסה, הכנסות, ותשלומים. ניתן לסנן לפי תאריכים, חדרים וסטטוס תשלום. הדוחות ניתנים לייצוא לאקסל או PDF.",
                "category": "reports",
                "tags": ["reports", "payments", "דוחות", "תשלומים"]
            },
            {
                "title": "ניהול חדרים",
                "content": "במסך ניהול החדרים ניתן לראות את סטטוס כל חדר (פנוי, תפוס, בניקיון), לעדכן מחירים, להגדיר סוגי חדרים ולנהל תחזוקה.",
                "category": "rooms",
                "tags": ["rooms", "חדרים", "תחזוקה"]
            },
            {
                "title": "תמיכה טכנית בעיות נפוצות",
                "content": "בעיות נפוצות: מערכת איטית - נקה cache של הדפדפן. שגיאת חיבור - בדוק חיבור לאינטרנט. לא מצליח להדפיס - בדוק הגדרות מדפסת. נתונים לא מתעדכנים - רענן את הדף.",
                "category": "troubleshooting",
                "tags": ["technical support", "תמיכה טכנית", "בעיות"]
            }
        ]
        
        for item in base_knowledge:
            self.items.append({
                "id": f"{item['category']}_{len(self.items)}",
                "title": item["title"],
                "content": item["content"],
                "category": item["category"],
                "tags": item["tags"]
            })
    
    def _calculate_relevance(self, query: str, item: Dict) -> float:
        """חישוב רלוונטיות פשוט על בסיס מילים"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        text = f"{item['title']} {item['content']} {' '.join(item.get('tags', []))}".lower()
        text_words = set(re.findall(r'\w+', text))
        
        # חישוב overlap
        common = query_words & text_words
        if not query_words:
            return 0.0
        
        return len(common) / len(query_words)
    
    async def add_item(
        self,
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        הוספת פריט חדש למאגר הידע
        """
        if tags is None:
            tags = []
        
        doc_id = f"{category}_{len(self.items)}"
        
        self.items.append({
            "id": doc_id,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags
        })
        
        self._save_to_file()
        return doc_id
    
    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        חיפוש במאגר הידע
        
        Args:
            query: שאלת החיפוש
            limit: מספר התוצאות המקסימלי
        
        Returns:
            רשימת תוצאות רלוונטיות
        """
        # חישוב רלוונטיות לכל פריט
        scored_items = []
        for item in self.items:
            score = self._calculate_relevance(query, item)
            if score > 0:
                scored_items.append((score, item))
        
        # מיון לפי רלוונטיות
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # החזרת התוצאות
        formatted_results = []
        for score, item in scored_items[:limit]:
            formatted_results.append({
                "content": item["content"],
                "metadata": {
                    "title": item["title"],
                    "category": item["category"],
                    "tags": ",".join(item.get("tags", []))
                },
                "distance": 1.0 - score  # המרה לדמיון (0 = זהה)
            })
        
        return formatted_results
    
    async def get_context_for_query(self, query: str, max_results: int = 3) -> str:
        """
        קבלת קונטקסט רלוונטי לשאלה
        
        Returns:
            מחרוזת עם הקונטקסט הרלוונטי
        """
        results = await self.search(query, limit=max_results)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result['metadata'].get('title', 'ללא כותרת')
            content = result['content']
            context_parts.append(f"{i}. {title}\n{content}\n")
        
        return "\n".join(context_parts)

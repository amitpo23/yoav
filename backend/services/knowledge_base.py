import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class KnowledgeBaseService:
    """
    שירות לניהול מאגר הידע (Knowledge Base) באמצעות ChromaDB
    """
    
    def __init__(self):
        self.db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # אתחול מודל ה-Embeddings
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # אתחול ChromaDB
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # יצירת או טעינת הקולקציה
        self.collection = self.client.get_or_create_collection(
            name="hotel_management_kb",
            metadata={"description": "Knowledge base for hotel management systems"}
        )
        
        # אתחול עם נתונים בסיסיים אם הקולקציה ריקה
        if self.collection.count() == 0:
            self._initialize_base_knowledge()
    
    def is_available(self) -> bool:
        """בדיקה אם השירות זמין"""
        return self.collection is not None
    
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
            self._add_item_sync(
                title=item["title"],
                content=item["content"],
                category=item["category"],
                tags=item["tags"]
            )
    
    def _add_item_sync(self, title: str, content: str, category: str, tags: List[str]):
        """הוספת פריט באופן סינכרוני (לאתחול)"""
        doc_id = f"{category}_{len(self.collection.get()['ids'])}"
        
        self.collection.add(
            documents=[content],
            metadatas=[{
                "title": title,
                "category": category,
                "tags": ",".join(tags)
            }],
            ids=[doc_id]
        )
    
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
        
        doc_id = f"{category}_{self.collection.count()}"
        
        self.collection.add(
            documents=[content],
            metadatas=[{
                "title": title,
                "category": category,
                "tags": ",".join(tags)
            }],
            ids=[doc_id]
        )
        
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
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
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

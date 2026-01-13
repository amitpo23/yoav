# Knowledge Base - מאגר ידע לבתי מלון

תיקייה זו מכילה את מאגר הידע של המערכת. המידע כאן משמש את ה-AI לתת תשובות מדויקות.

## מבנה

הנתונים נשמרים אוטומטית ב-ChromaDB בתיקייה `chroma_db/` (נוצרת אוטומטית).

## נתונים ראשוניים

המערכת מגיעה עם מידע בסיסי על:
- התחברות למערכת
- ניהול הזמנות
- דוחות ותשלומים
- ניהול חדרים
- פתרון בעיות טכניות נפוצות

## הוספת מידע חדש

### דרך API:

```python
import requests

data = {
    "title": "שינוי מחיר חדר",
    "content": "לשינוי מחיר חדר, היכנס לתפריט 'ניהול חדרים', בחר את החדר, לחץ על 'עריכה', עדכן את המחיר ולחץ 'שמור'.",
    "category": "rooms",
    "tags": ["מחירים", "חדרים", "עריכה"]
}

response = requests.post(
    "http://localhost:8000/api/knowledge-base/add",
    json=data
)
print(response.json())
```

### דרך קוד Python:

```python
from services.knowledge_base import KnowledgeBaseService

kb = KnowledgeBaseService()

await kb.add_item(
    title="כותרת",
    content="תוכן המאמר...",
    category="קטגוריה",
    tags=["תגית1", "תגית2"]
)
```

## קטגוריות מומלצות

- `authentication` - התחברות ואימות
- `reservations` - הזמנות וחדרים
- `reports` - דוחות ותשלומים
- `rooms` - ניהול חדרים
- `troubleshooting` - פתרון בעיות
- `features` - תכונות המערכת
- `integrations` - אינטגרציות

## טיפים למידע איכותי

1. **כותרות ברורות** - השתמש בכותרות תיאוריות
2. **תוכן מפורט** - כלול צעדים מדויקים
3. **תגיות רלוונטיות** - הוסף תגיות שיעזרו בחיפוש
4. **דוגמאות** - כלול דוגמאות מעשיות
5. **עדכון שוטף** - עדכן מידע לא רלוונטי

## חיפוש במאגר

```bash
curl "http://localhost:8000/api/knowledge-base/search?query=איך+מדפיסים+דוח&limit=5"
```

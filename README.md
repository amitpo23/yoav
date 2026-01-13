# מערכת תמיכה טכנית AI לבתי מלון 🏨

מערכת מתקדמת לתמיכה טכנית באמצעות בינה מלאכותית, מיועדת לסייע ללקוחות של מערכות ניהול בתי מלון.

## תכונות עיקריות ✨

- 🤖 **צ'אטבוט AI מתקדם** - מבוסס על GPT-4 לתמיכה טכנית חכמה
- 📚 **מאגר ידע (Knowledge Base)** - מערכת חיפוש סמנטי במסמכי תמיכה
- 💬 **ממשק צ'אט מודרני** - חווית משתמש אינטואיטיבית ומהירה
- 🔍 **חיפוש חכם** - מציאת מידע רלוונטי באופן אוטומטי
- 📱 **רספונסיבי** - פועל בצורה מושלמת על כל המכשירים

## מבנה הפרויקט 📁

```
yoav/
├── backend/              # שרת Backend (FastAPI + Python)
│   ├── services/        # שירותים (LLM, Knowledge Base, Chat Manager)
│   ├── main.py          # נקודת הכניסה הראשית
│   ├── requirements.txt # תלויות Python
│   └── .env.example     # דוגמת קובץ הגדרות
│
├── frontend/            # אפליקציית Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/  # קומפוננטות React
│   │   ├── services/    # שירותי API
│   │   └── App.tsx      # קומפוננטה ראשית
│   ├── package.json     # תלויות Node.js
│   └── .env.example     # דוגמת קובץ הגדרות
│
└── knowledge-base/      # נתוני מאגר הידע
```

## התקנה והרצה 🚀

### דרישות מקדימות

- Python 3.9 ומעלה
- Node.js 18 ומעלה
- מפתח API של OpenAI

### התקנת Backend

```bash
cd backend

# יצירת סביבה וירטואלית
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate  # Windows

# התקנת תלויות
pip install -r requirements.txt

# הגדרת משתני סביבה
cp .env.example .env
# ערוך את קובץ .env והוסף את מפתח ה-API שלך

# הרצת השרת
python main.py
```

השרת יעלה על: http://localhost:8000

### התקנת Frontend

```bash
cd frontend

# התקנת תלויות
npm install

# הגדרת משתני סביבה
cp .env.example .env

# הרצת אפליקציית הפיתוח
npm start
```

האפליקציה תעלה על: http://localhost:3000

## שימוש במערכת 💡

### צ'אט בסיסי

1. פתח את הדפדפן והיכנס ל-http://localhost:3000
2. הקלד את השאלה שלך בשדה הטקסט
3. המערכת תחפש במאגר הידע ותחזיר תשובה מותאמת

### הוספת מידע למאגר הידע

```python
import requests

data = {
    "title": "כותרת המאמר",
    "content": "תוכן המאמר...",
    "category": "קטגוריה",
    "tags": ["תגית1", "תגית2"]
}

response = requests.post(
    "http://localhost:8000/api/knowledge-base/add",
    json=data
)
```

### API Endpoints

#### POST /api/chat
שליחת הודעה לצ'אטבוט

**Request:**
```json
{
  "message": "איך מתחברים למערכת?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "להתחברות למערכת...",
  "session_id": "unique-session-id",
  "sources": [...]
}
```

#### GET /api/chat/history/{session_id}
קבלת היסטוריית שיחה

#### POST /api/knowledge-base/add
הוספת מידע למאגר הידע

#### GET /api/knowledge-base/search
חיפוש במאגר הידע

## טכנולוגיות 🛠️

### Backend
- **FastAPI** - פריימוורק web מהיר ומודרני
- **OpenAI GPT-4** - מודל שפה מתקדם
- **ChromaDB** - מסד נתונים וקטורי לחיפוש סמנטי
- **LangChain** - כלי לבניית אפליקציות LLM
- **Sentence Transformers** - מודלים ל-embeddings

### Frontend
- **React 18** - ספריית UI מודרנית
- **TypeScript** - JavaScript עם טיפוסים
- **Axios** - לקוח HTTP
- **CSS3** - עיצוב מתקדם

## אבטחה 🔒

- מפתחות API נשמרים בקבצי `.env` ולא בגיט
- CORS מוגדר לדומיינים ספציפיים בפרודקשן
- כל הקלטים עוברים ולידציה
- Sessions מנוהלים באופן מאובטח

## פיצ'רים עתידיים 🔮

- [ ] אימות משתמשים
- [ ] תמיכה במספר שפות
- [ ] ייצוא היסטוריית שיחות
- [ ] דוחות ואנליטיקה
- [ ] אינטגרציה עם מערכות CRM
- [ ] תמיכה בקבצים ותמונות

## תמיכה 📞

לשאלות ובעיות, אנא צור issue בגיטהאב או צור קשר דרך:
- Email: support@example.com
- טלפון: 03-1234567

## רישיון 📄

MIT License - ראה קובץ LICENSE לפרטים

## תרומה 🤝

נשמח לתרומות! אנא:
1. צור Fork של הפרויקט
2. צור Branch חדש (`git checkout -b feature/AmazingFeature`)
3. בצע Commit לשינויים (`git commit -m 'Add some AmazingFeature'`)
4. בצע Push ל-Branch (`git push origin feature/AmazingFeature`)
5. פתח Pull Request

---

נבנה עם ❤️ למען שירות לקוחות טוב יותר
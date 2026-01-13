# מדריך הרצה מהירה 🚀

## התקנה מהירה

### שלב 1: Clone הפרויקט
```bash
git clone <repository-url>
cd yoav
```

### שלב 2: הגדרת Backend

```bash
cd backend

# צור סביבה וירטואלית
python -m venv venv

# הפעל את הסביבה
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate     # Windows

# התקן תלויות
pip install -r requirements.txt

# צור קובץ .env
cp .env.example .env

# ערוך את .env והוסף את מפתח OpenAI שלך:
# OPENAI_API_KEY=sk-...
```

### שלב 3: הגדרת Frontend

```bash
cd ../frontend

# התקן תלויות
npm install

# צור קובץ .env
cp .env.example .env
```

### שלב 4: הרצת המערכת

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # הפעל את הסביבה
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

המערכת תהיה זמינה ב:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## הרצה עם Docker

```bash
# הוסף את מפתח ה-API כמשתנה סביבה
export OPENAI_API_KEY=sk-...

# הרץ את המערכת
docker-compose up
```

## בדיקה ראשונית

1. פתח את הדפדפן והיכנס ל-http://localhost:3000
2. נסה לשאול: "איך מתחברים למערכת?"
3. המערכת תחזיר תשובה מבוססת על מאגר הידע

## פתרון בעיות נפוצות

### Backend לא עולה
- ודא שיש לך Python 3.9+
- בדוק שמפתח ה-OpenAI API תקין
- הפעל: `pip install -r requirements.txt` שוב

### Frontend לא עולה
- ודא שיש לך Node.js 18+
- מחק את node_modules והתקן שוב: `rm -rf node_modules && npm install`

### שגיאת חיבור ל-API
- ודא שה-Backend רץ על port 8000
- בדוק את קובץ .env ב-Frontend שמכיל: REACT_APP_API_URL=http://localhost:8000

# UnstructIQ

AI-powered data structuring and visualization platform.

## Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Chart.js
- **Backend**: FastAPI, Pandas, Claude AI
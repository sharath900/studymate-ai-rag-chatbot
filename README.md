# StudyMate AI — Smart Notes Chatbot using RAG

StudyMate AI is a Django-based smart notes chatbot that allows users to upload PDF study material and ask questions from the uploaded notes. The system uses a RAG-style workflow to retrieve relevant content from notes and generate simple answers using Gemini AI.

## Features

- User registration and login
- Upload PDF study notes
- Extract text from uploaded PDFs
- Split notes into smaller chunks
- Search relevant content from selected PDF
- Ask questions from uploaded notes
- AI-generated answers using Gemini API
- Delete uploaded notes
- Clean and responsive Bootstrap UI

## Tech Stack

- Python
- Django
- HTML
- Bootstrap 5
- SQLite
- PyPDF
- Scikit-learn
- Gemini API

## How It Works

1. User uploads a PDF note.
2. The system extracts text from the PDF.
3. The extracted text is divided into smaller chunks.
4. When the user asks a question, the system searches for the most relevant chunks.
5. The relevant content is sent to Gemini AI.
6. Gemini generates an answer based on the uploaded notes.
7. ## Author

Sharath Kumar  
GitHub: sharath900

   

## Project Structure

```text
chatbot/
│
├── chatbot_project/
│   ├── settings.py
│   ├── urls.py
│
├── home/
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│
├── notes/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── rag_utils.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── upload_notes.html
│   ├── study_chat.html
│
├── media/
├── static/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md

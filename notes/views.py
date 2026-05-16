from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from dotenv import load_dotenv
from google import genai
import os

from .models import UploadedNote, NoteChunk, StudyChatMessage
from .rag_utils import extract_text_from_pdf, split_text_into_chunks, search_relevant_chunks


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@login_required(login_url='login')
def upload_notes(request):
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf_file")
        title = request.POST.get("title")

        if not pdf_file:
            messages.error(request, "Please upload a PDF file.")
            return redirect("upload_notes")

        if not title:
            title = pdf_file.name

        if not pdf_file.name.lower().endswith(".pdf"):
            messages.error(request, "Only PDF files are allowed.")
            return redirect("upload_notes")

        try:
            note = UploadedNote.objects.create(
                user=request.user,
                title=title,
                pdf_file=pdf_file
            )

            pdf_path = note.pdf_file.path

            extracted_text = extract_text_from_pdf(pdf_path)

            if not extracted_text.strip():
                messages.error(request, "Could not extract text from this PDF. Try another PDF.")
                note.delete()
                return redirect("upload_notes")

            note.extracted_text = extracted_text
            note.save()

            chunks = split_text_into_chunks(extracted_text)

            for index, chunk in enumerate(chunks):
                NoteChunk.objects.create(
                    note=note,
                    chunk_text=chunk,
                    chunk_index=index
                )

            messages.success(request, "Notes uploaded and processed successfully.")
            return redirect("study_chat")

        except Exception as e:
            print("PDF UPLOAD ERROR:", e)
            messages.error(request, "Something went wrong while processing the PDF.")
            return redirect("upload_notes")

    notes = UploadedNote.objects.filter(user=request.user).order_by("-uploaded_at")

    return render(request, "upload_notes.html", {
        "notes": notes
    })


@login_required(login_url='login')
def study_chat(request):
    question = ""
    answer = ""
    selected_note = None

    notes = UploadedNote.objects.filter(user=request.user).order_by("-uploaded_at")

    if request.method == "POST":
        question = request.POST.get("question")
        note_id = request.POST.get("note_id")

        if not note_id:
            messages.error(request, "Please select one uploaded note.")
            return redirect("study_chat")

        if not question:
            messages.error(request, "Please type a question.")
            return redirect("study_chat")

        try:
            selected_note = UploadedNote.objects.get(id=note_id, user=request.user)
        except UploadedNote.DoesNotExist:
            messages.error(request, "Selected note was not found.")
            return redirect("study_chat")

        note_chunks = NoteChunk.objects.filter(note=selected_note)

        if not note_chunks.exists():
            messages.error(request, "This note has no processed content. Please upload again.")
            return redirect("upload_notes")

        relevant_chunks = search_relevant_chunks(question, note_chunks, top_k=10)

        if not relevant_chunks:
            answer = """
            <p>I could not find related content in the selected note.</p>
            <p>Try asking the question using words from your PDF.</p>
            """
        else:
            context = "\n\n".join(relevant_chunks)

            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
You are StudyMate AI, a smart notes chatbot.

You must answer the student's question using only the selected uploaded note context given below.

Rules:
- Use only the given notes context.
- If part of the answer is available in the notes, answer that part.
- Only say "I could not find this answer in your uploaded notes" for the missing part.
- Explain in simple student-friendly English.
- Use clean HTML format.
- Use <h5> for headings.
- Use <p> for paragraphs.
- Use <ul><li> for bullet points.
- Use <strong> for important words.
- Do not use markdown symbols like ** or #.
- Do not mention "context" in the final answer.
- Start directly with the answer.

Selected note title:
{selected_note.title}

Uploaded notes content:
{context}

Student question:
{question}
"""
                )

                answer = response.text

                StudyChatMessage.objects.create(
                    user=request.user,
                    question=question,
                    answer=answer
                )

            except Exception as e:
                print("STUDY CHAT GEMINI ERROR:", e)
                answer = "Sorry bro, I could not get Gemini response. Check terminal error."

    return render(request, "study_chat.html", {
        "question": question,
        "answer": answer,
        "notes": notes,
        "selected_note": selected_note,
    })

@login_required(login_url='login')
def delete_note(request, note_id):
    try:
        note = UploadedNote.objects.get(id=note_id, user=request.user)
        note.delete()
        messages.success(request, "Note deleted successfully.")
    except UploadedNote.DoesNotExist:
        messages.error(request, "Note not found.")

    return redirect("upload_notes")
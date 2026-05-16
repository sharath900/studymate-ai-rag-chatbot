from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from dotenv import load_dotenv
from google import genai
import os

from .models import ChatMessage

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return redirect('login')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "register.html")


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


@login_required(login_url='login')
def chatbot(request):
    user_message = ""
    bot_response = ""

    if request.method == "POST":
        user_message = request.POST.get("message")

        if user_message:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
You are an AI assistant inside a Django chatbot web app.

Answer the user's question in clean HTML format.

Rules:
- Use <h5> for headings
- Use <p> for paragraphs
- Use <ul><li> for bullet points
- Use <strong> for important words
- Do not use markdown symbols like ** or #
- Keep the answer simple and easy to understand

User question:
{user_message}
"""
                )

                bot_response = response.text

                ChatMessage.objects.create(
                    user=request.user,
                    user_message=user_message,
                    bot_response=bot_response
                )

            except Exception as e:
                print("GEMINI ERROR:", e)
                bot_response = "Sorry bro, I could not get Gemini response. Check terminal error."

        else:
            bot_response = "Please type something."

    return render(request, 'chatbot.html', {
        'user_message': user_message,
        'bot_response': bot_response
    })
import json
from difflib import get_close_matches
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import os

# Utility functions
def load_knowledge_base(file_path: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {"questions": []}

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.8)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None

def speak(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Login and Signup GUI
def login_signup():
    def signup():
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            if not os.path.exists('users.json'):
                with open('users.json', 'w') as file:
                    json.dump({}, file)

            with open('users.json', 'r') as file:
                users = json.load(file)

            if username in users:
                messagebox.showerror("Error", "Username already exists")
            else:
                users[username] = password
                with open('users.json', 'w') as file:
                    json.dump(users, file)
                messagebox.showinfo("Success", "Account created successfully")
        else:
            messagebox.showerror("Error", "Please fill all fields")

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            if os.path.exists('users.json'):
                with open('users.json', 'r') as file:
                    users = json.load(file)

                if username in users and users[username] == password:
                    messagebox.showinfo("Success", "Login successful")
                    login_window.destroy()
                    chat_bot()
                else:
                    messagebox.showerror("Error", "Invalid username or password")
            else:
                messagebox.showerror("Error", "No users found. Please sign up first.")
        else:
            messagebox.showerror("Error", "Please fill all fields")

    login_window = tk.Tk()
    login_window.title("Login / Signup")
    login_window.geometry("400x300")
    login_window.configure(bg="black")

    tk.Label(login_window, text="Username", fg="green", bg="black").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password", fg="green", bg="black").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    tk.Button(login_window, text="Login", command=login, bg="green", fg="black").pack(pady=10)
    tk.Button(login_window, text="Signup", command=signup, bg="green", fg="black").pack(pady=10)

    login_window.mainloop()

# Chatbot GUI
def chat_bot():
    knowledge_base = load_knowledge_base('knowledge_base.json')

    def send_message():
        user_message = user_input.get()
        if not user_message.strip():
            return

        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"You: {user_message}\n", "user")

        best_match = find_best_match(user_message, [q["question"] for q in knowledge_base["questions"]])
        if best_match:
            answer = get_answer_for_question(best_match, knowledge_base)
            response = f"Bot: {answer}\n"
        else:
            response = "Bot: I don't know the answer. Can you teach me?\n"

        chat_log.insert(tk.END, response, "bot")
        chat_log.config(state=tk.DISABLED)
        speak(response)

        if not best_match:
            def save_new_answer():
                new_answer = answer_input.get()
                if new_answer.strip():
                    knowledge_base["questions"].append({"question": user_message, "answer": new_answer})
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    chat_log.config(state=tk.NORMAL)
                    chat_log.insert(tk.END, "Bot: Thank you! I learned a new response!\n", "bot")
                    chat_log.config(state=tk.DISABLED)
                    speak("Thank you! I learned a new response!")
                answer_window.destroy()

            answer_window = tk.Toplevel()
            answer_window.title("Teach the Bot")
            tk.Label(answer_window, text="Provide an answer:").pack(pady=5)
            answer_input = tk.Entry(answer_window, width=50)
            answer_input.pack(pady=5)
            tk.Button(answer_window, text="Save", command=save_new_answer).pack(pady=5)

    root = tk.Tk()
    root.title("ChatBot")
    root.geometry("500x600")
    root.configure(bg="black")

    chat_log = tk.Text(root, state=tk.DISABLED, bg="black", fg="green", wrap=tk.WORD)
    chat_log.tag_config("user", foreground="green")
    chat_log.tag_config("bot", foreground="white")
    chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    user_input = tk.Entry(root, bg="black", fg="green")
    user_input.pack(padx=10, pady=10, fill=tk.X)

    send_button = tk.Button(root, text="Send", bg="green", fg="black", command=send_message)
    send_button.pack(pady=5)

    root.mainloop()

if __name__ == '_main_':
    login_signup()
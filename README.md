# Quiznet-Django

Quiznet-Django is a web-based quiz platform built with Django, designed to deliver personalized quizzes, track user progress, and visualize performance analytics. This project leverages AI to generate quizzes tailored to user strengths and weaknesses, with a modern UI and interactive charts.

## Features

- **AI-Powered Quiz Generation:** Dynamically creates quiz questions based on user-selected topics and difficulty levels.
- **User Authentication:** Secure signup, login, and session management using Django Allauth.
- **Quiz History:** Users can review their past quizzes and scores.
- **Performance Analytics:** Interactive charts display user scores, trends, and insights over time (powered by Chart.js).
- **Responsive Design:** Modern, mobile-friendly interface with custom backgrounds and animations.
- **Multiple Question Types:** Supports MCQ, Fill-in-the-Blank, True/False, and Logical Reasoning formats.

## Tech Stack

- **Backend:** Django, Python 3.13
- **Frontend:** HTML, CSS, JavaScript (Chart.js, Three.js, Vanta.js for effects)
- **Authentication:** Django Allauth
- **Database:** SQLite (default, easily configurable)
- **AI Integration:** Quiz generation logic is customizable for external AI APIs

## Getting Started

### Prerequisites

- Python 3.13.x (see `runtime.txt`)
- Django (see requirements)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/karan95427/Quiznet-Django.git
   cd Quiznet-Django
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   - Copy `.env.example` to `.env` and set your environment variables:
     - `django_secret_key`
     - (Optional) `GEMINI_API_KEY` or other AI provider API keys for quiz generation.

4. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the app:**
   Visit `http://localhost:8000/`

## Usage

- **Signup/Login:** Access via the homepage. Social login is available if configured.
- **Quiz:** Choose topic and difficulty, start quiz, and receive instant feedback.
- **History & Analytics:** Track and visualize your score trends from the dashboard.

## Configuration

Edit `Django/settings.py` for custom settings, such as static file handling, database, and Allauth options.

## Folder Structure

- `aiquiz/` – Main Django app (views, models, templates, static)
- `Django/` – Project settings, URLs, WSGI/ASGI config
- `templates/` – HTML templates
- `static/aiquiz/` – CSS, JS, images

## License

This project does not yet specify a license. See repository for updates.

## Author

Developed by [karan95427](https://github.com/karan95427)

---
Feel free to open an issue or PR for contributions or bug reports!

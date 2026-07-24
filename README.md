# Course Content Generator — Day 88, 89 and 90

This full Django project covers Questions 1 to 60.
Question numbers are included as comments inside the code.

## Questions 1 to 4 — Setup commands

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
django-admin startproject content_gen .
python manage.py startapp generator
```

The project and app are already created in this ZIP.

## Questions 5 to 8 — Files

```text
content_gen/settings.py
generator/models.py
generator/admin.py
```

## Question 9 — Migrations

```powershell
python manage.py makemigrations generator
python manage.py migrate
```

## Question 10 — Superuser

```powershell
python manage.py createsuperuser
```

## Questions 11 to 20

```text
generator/forms.py
generator/services.py
generator/views.py
```

## Questions 21 to 30

```text
generator/models.py
generator/services.py
generator/views.py
```

## Questions 31 to 40

```text
generator/views.py
generator/urls.py
generator/templates/generator/
```

Student test flow:

1. Login as teacher.
2. Generate a course topic.
3. Open Student Dashboard.
4. Open the generated content.
5. Answer the quiz.
6. Submit and check the score.

## Question 41 — ReportLab

```powershell
pip install reportlab
```

## Questions 42 to 50

PDF export code is in:

```text
generator/views.py
```

## Questions 51 to 54

```powershell
python manage.py test
python manage.py loaddata sample_data
```

Tests:

```text
generator/tests.py
```

Fixture:

```text
generator/fixtures/sample_data.json
```

## Questions 55 to 60 — Production

Copy the environment file:

```powershell
copy .env.example .env
```

Add the real Gemini API key inside `.env`.

```text
GEMINI_API_KEY=your-real-key
```

For production:

```text
DEBUG=False
ALLOWED_HOSTS=your-domain.onrender.com
```

Collect static files:

```powershell
python manage.py collectstatic --noinput
```

Run with Gunicorn:

```powershell
gunicorn content_gen.wsgi:application
```

## Complete local run

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Teacher page:

```text
http://127.0.0.1:8000/teacher/generate/
```

Admin page:

```text
http://127.0.0.1:8000/admin/
```

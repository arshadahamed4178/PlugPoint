# 🛒 PlugPoint – Django E-Commerce Platform

PlugPoint is a full-stack e-commerce web application built with Django. It provides a complete shopping workflow including user authentication, product catalog, cart management, and order placement using SQLite as the database.

## 🛠️ Tech Stack
Django 4.2, Python, SQLite, HTML, CSS, JavaScript, Django Templates, Pillow

## ✨ Features
- User registration & login  
- Product listing with images  
- Add to cart functionality  
- Order placement workflow  
- Dynamic templates using Django ORM  
- Session-based cart management  

## ⚙️ Setup & Run

```bash
git clone https://github.com/yourusername/plugpoint.git
cd plugpoint

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

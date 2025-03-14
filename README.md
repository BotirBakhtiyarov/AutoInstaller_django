# AutoInstaller

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-4.2.20-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**AutoInstaller** is a Django-based web application designed to manage, purchase, and automatically install software applications. It features a user-friendly frontend for browsing apps, WeChat payment integration for purchases, and a RESTful API to trigger installation scripts programmatically. The project supports both local development and Docker deployment.

---

## Features

- **App Management**: Admins can upload apps with ZIP files, icons, screenshots, and installation scripts via a management interface.
- **WeChat Payment**: Users can purchase paid apps using WeChat QR code payments.
- **Automatic Installation**: Trigger installation scripts stored in app records via a web interface or API.
- **API Access**: RESTful endpoint to initiate installations without the frontend.
- **Docker Support**: Deploy the app with Docker Compose for consistent environments.

---

## Project Structure

```
AutoInstaller_for-company/
├── .env              # Environment variables (e.g., WeChat credentials)
├── AutoInstaller/
│   ├── settings.py   # Django settings with .env integration
│   ├── urls.py      # Root URL configuration
│   ├── Wechat_cert/ # Directory for WeChat certificates
│   │   ├── cert.pem
│   │   └── key.pem
│   └── ...
├── Installer/        # App for user-facing features
│   ├── models.py    # App and UserPurchase models
│   ├── views.py     # Views including payment and API
│   ├── urls.py      # App-specific URL routes
│   └── ...
├── Management/       # App for admin management
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile        # Docker image definition
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)
- PostgreSQL (optional, replace SQLite if desired)
- WeChat Merchant Account (for payment integration)

---

## Installation

### Local Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/BotirBakhtiyarov/AutoInstaller_django.git
   cd AutoInstaller_django
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_NAME=db.sqlite3
   ALLOWED_HOSTS=localhost,127.0.0.1

   # WeChat Payment Settings
   WECHAT_APP_ID=your-app-id
   WECHAT_API_KEY=your-api-key
   WECHAT_MCH_ID=your-merchant-id
   WECHAT_MCH_CERT=Wechat_cert/cert.pem
   WECHAT_MCH_KEY=Wechat_cert/key.pem
   ```
   - Replace values with your own (e.g., WeChat credentials).
   - Ensure `Wechat_cert/cert.pem` and `Wechat_cert/key.pem` exist in `AutoInstaller/Wechat_cert/`.

5. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Server**
   ```bash
   python manage.py runserver
   ```
   - Access at `http://localhost:8000/`.

---

### Docker Setup

1. **Ensure Docker is Installed**
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop) or Docker CLI.

2. **Configure `.env`**
   - Use the same `.env` file as above.

3. **Build and Run**
   ```bash
   docker-compose up --build
   ```
   - Access at `http://localhost:8000/`.
   - View logs: `docker-compose logs web`.

4. **Apply Migrations in Docker**
   ```bash
   docker exec -it <web_container_id> python manage.py migrate
   docker exec -it <web_container_id> python manage.py createsuperuser
   ```

5. **Stop Containers**
   ```bash
   docker-compose down
   ```

---

## Usage

### Frontend
- **Browse Apps**: Visit `/app/<app_name>/` to view app details, screenshots, and purchase options.
- **Purchase**: Click "Pay" to generate a WeChat QR code for paid apps. After payment, download and install buttons appear.
- **Admin Panel**: Access `/management/admin/` (staff only) to add/edit apps.

### API
- **Endpoint**: `/api/install/<app_name>/`
- **Method**: `POST`
- **Authentication**: Token-based (optional)
- **Example Request**:
  ```bash
  curl -X POST http://localhost:8000/api/install/Auto%20Revit%202022/ \
       -H "Authorization: Token <your_token>"
  ```
- **Response** (Success):
  ```json
  {
    "status": "success",
    "message": "Installation started for Auto Revit 2022",
    "output": "<script output>"
  }
  ```
- **Response** (Error):
  ```json
  {
    "error": "Script execution failed",
    "details": "<error message>"
  }
  ```

- **Generate Token**:
  ```bash
  python manage.py shell
  ```
  ```python
  from rest_framework.authtoken.models import Token
  from django.contrib.auth.models import User
  user = User.objects.get(username='your_username')
  token = Token.objects.create(user=user)
  print(token.key)
  ```

---

## Configuration

### Environment Variables
Stored in `.env`:
- `SECRET_KEY`: Django secret key.
- `DEBUG`: Set to `True` for development, `False` for production.
- `DATABASE_NAME`: SQLite database file (or configure PostgreSQL).
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts.
- `WECHAT_*`: WeChat payment credentials and certificate paths.

### Settings
- `MEDIA_ROOT`: Stores uploaded files (e.g., `/srv/AutoInstaller/media/` in Docker).
- `LOGGING`: Logs to console and `debug.log` for debugging.

---

## Development

### Adding an App
1. Log in as staff at `/management/login/`.
2. Go to `/management/add-app/`.
3. Upload a ZIP file containing the app script (e.g., `install.sh` or `install.bat`), icon, and screenshots.

### Customizing Scripts
- Scripts are stored in `App.script` (full path, e.g., `/srv/AutoInstaller/unzipped/<app_name>/install.sh`).
- Ensure scripts are executable (`chmod +x install.sh` in Docker).

---

## Troubleshooting

- **Payment Fails in Docker**:
  - Check `debug.log` or `docker-compose logs web` for errors.
  - Verify `Wechat_cert/` files are mounted (`ls -l /srv/AutoInstaller/Wechat_cert/` in container).
  - Test WeChat API connectivity: Add `requests.get('https://api.weixin.qq.com/')` in `payment_view`.

- **API Errors**:
  - Ensure `App.script` paths are valid.
  - Check logs for `Script not found` or execution errors.

---

## Deployment

For production:
1. Set `DEBUG=False` in `.env`.
2. Use a WSGI server (e.g., Gunicorn):
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "AutoInstaller.wsgi:application"]
   ```
3. Configure HTTPS with Nginx and a certificate (e.g., Let’s Encrypt).
4. Update `notify_url` in `payment_view` to your domain.

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/xyz`).
3. Commit changes (`git commit -m "Add XYZ feature"`).
4. Push to the branch (`git push origin feature/xyz`).
5. Open a Pull Request.

---

### Notes on `.env`
- **Why `.env`**: Replaces `config.py` for better security and flexibility. Use `python-decouple` to load `.env` variables in `settings.py`:
  ```bash
  pip install python-decouple
  ```
  ```python
  # AutoInstaller/settings.py
  from decouple import config

  SECRET_KEY = config('SECRET_KEY')
  DEBUG = config('DEBUG', default=False, cast=bool)
  DATABASE_NAME = config('DATABASE_NAME')
  ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
  WECHAT_APP_ID = config('WECHAT_APP_ID')
  WECHAT_API_KEY = config('WECHAT_API_KEY')
  WECHAT_MCH_ID = config('WECHAT_MCH_ID')
  WECHAT_MCH_CERT = config('WECHAT_MCH_CERT')
  WECHAT_MCH_KEY = config('WECHAT_MCH_KEY')
  ```

# AutoInstaller

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-4.2.20-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

**AutoInstaller** is a Django-based web application designed to manage and install software applications. It features a frontend for browsing and purchasing apps with WeChat payment integration, an admin interface for app management, and an API to trigger installations programmatically. On Windows, installations are executed via a custom protocol (`myapp://`) handled by `LocalApp.exe`, which can be triggered from the frontend or a command-line batch file.

---

## Features

- **App Management**: Admins can upload apps with ZIP files, icons, screenshots, and installation scripts via `/management/admin/`.
- **WeChat Payment**: Users can purchase paid apps using WeChat QR code payments.
- **Frontend Installation**: Click "安装" (Install) to trigger app installation via a custom protocol.
- **API Installation**: Use `install_app <app_name>` in CMD to trigger installations via the API and `LocalApp.exe`.
- **Docker Support**: Deploy the server with Docker Compose.

---

## Project Structure

```
AutoInstaller_for-company/
├── .env              # Environment variables (DB, WeChat credentials)
├── AutoInstaller/
│   ├── settings.py   # Django settings with .env integration
│   ├── urls.py      # Root URL configuration
│   └── ...
├── Installer/        # App for user-facing features
│   ├── models.py    # App model
│   ├── views.py     # API and payment views
│   ├── urls.py      # App-specific routes
│   └── templates/   # Frontend templates
│       └── app_detail.html
├── Management/       # Admin management app
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile        # Docker image definition
├── requirements.txt  # Python dependencies
├── install_app.bat   # Batch file for API-triggered installs
├── LocalApp.exe      # Compiled installer (Windows)
└── README.md         # This file
```

---

## Prerequisites

- **Server**:
  - Python 3.10+
  - Docker (optional, for containerized deployment)
  - PostgreSQL (running on `db-host`)
  - WeChat Merchant Account (for payments)

- **Client (Windows)**:
  - `LocalApp.exe` in `C:\localapp\`
  - `install_app.bat` in PATH (e.g., `C:\Users\<username>\` or `C:\Windows\System32`)
  - Network access to `\\localhost\apps\` for installers

---

## Installation

### Server Setup

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

4. **Set Up `.env`**
   Create `.env` in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database settings
   DB_NAME=app_database
   DB_USER=admin
   DB_PASSWORD=admin
   DB_HOST=host
   DB_PORT=5432

   # WeChat Payment Settings
   WECHAT_APP_ID=your-app-id
   WECHAT_API_KEY=your-api-key
   WECHAT_MCH_ID=your-merchant-id
   WECHAT_MCH_CERT=Wechat_cert/cert.pem
   WECHAT_MCH_KEY=Wechat_cert/key.pem
   ```

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

#### Docker Setup
1. **Build and Run**
   ```bash
   docker-compose up --build
   ```
2. **Apply Migrations**
   ```bash
   docker exec -it <web_container_id> python manage.py migrate
   docker exec -it <web_container_id> python manage.py createsuperuser
   ```

---

### Client Setup (Windows)

1. **Place `LocalApp.exe`**
   - Copy `LocalApp.exe` to `C:\localapp\`.
   - Ensure it’s compiled from `install_app.py` with `psycopg2` bundled:
     ```bash
     pyinstaller --onefile --console --hidden-import=psycopg2 install_app.py -n LocalApp
     ```

2. **Register Custom Protocol**
   - Save as `myapp.reg`:
     ```reg
     Windows Registry Editor Version 5.00

     [HKEY_CLASSES_ROOT\myapp]
     @="URL:MyApp Protocol"
     "URL Protocol"=""

     [HKEY_CLASSES_ROOT\myapp\shell]
     [HKEY_CLASSES_ROOT\myapp\shell\open]
     [HKEY_CLASSES_ROOT\myapp\shell\open\command]
     @="\"C:\\localapp\\LocalApp.exe\" \"%1\""
     ```
   - Double-click to import.

3. **Set Up `install_app.bat`**
   - Save in `C:\Users\<username>\install_app.bat`:
     ```bat
     @echo off
     setlocal EnableDelayedExpansion

     if "%~1"=="" (
         echo Usage: %0 ^<app_name^>
         exit /b 1
     )

     set "APP_NAME=%~1"
     set "API_URL=http://localhost:8000/api/install/%APP_NAME%/"

     echo Calling API for %APP_NAME%...
     curl -X POST "%API_URL%" > response.json

     for /f "tokens=*" %%i in ('powershell -Command "Get-Content response.json | ConvertFrom-Json | Select-Object -ExpandProperty install_url"') do (
         set "INSTALL_URL=%%i"
     )

     if "!INSTALL_URL!"=="" (
         echo Error: No install URL returned from API. Check response.json.
         type response.json
         exit /b 1
     )

     echo Triggering installation for %APP_NAME% with URL: !INSTALL_URL!...
     "C:\localapp\LocalApp.exe" "!INSTALL_URL!"

     del response.json
     endlocal
     ```
   - Add to `PATH`:
     - Move to `C:\Windows\System32\` (requires admin):
       ```cmd
       move C:\Users\<username>\install_app.bat C:\Windows\System32\
       ```
     - Or update `PATH`:
       ```cmd
       setx PATH "%PATH%;C:\Users\<username>"
       ```

---

## Usage

### Frontend
- **Browse Apps**: Visit `/app/<app_name>/` to view details and purchase.
- **Install**: Click "安装" to trigger `myapp://install/<app_name>`, launching `LocalApp.exe`.

### API
- **Command**: Open CMD and run:
  ```cmd
  install_app WeChat
  ```
- **Response**: Triggers `LocalApp.exe` to install `WeChat` from `\\10.20.1.201\apps\`.

### Admin
- **Add Apps**: Log in at `/management/admin/` to upload apps with scripts.

---

## How It Works

1. **API Call**: `install_app <app_name>` calls `http://localhost:8000/api/install/<app_name>/`, returning `{"install_url": "myapp://install/<app_name>"}`.
2. **Batch File**: `install_app.bat` extracts the `install_url` and runs `LocalApp.exe` with it.
3. **LocalApp.exe**: Fetches the script path from `app_database` and executes it from `\\localhost\apps\`.

---

## Troubleshooting

- **API Error**:
  - Check `debug.log` for `No App matches the given query`.
  - Add apps via `/management/admin/`.

- **Install Fails**:
  - Test: `C:\localapp\LocalApp.exe myapp://install/WeChat`.
  - Verify `\\localhost\apps\<script_path>` accessibility.

- **Command Not Found**:
  - Ensure `install_app.bat` is in `PATH`:
    ```cmd
    echo %PATH%
    ```

---

## Deployment

- **Production**:
  - Set `DEBUG=False` in `.env`.
  - Use Gunicorn: `CMD ["gunicorn", "--bind", "0.0.0.0:8000", "AutoInstaller.wsgi:application"]` in `Dockerfile`.
  - Secure with Nginx and HTTPS.

- **Client**: Distribute `LocalApp.exe` and `install_app.bat` with instructions.

---

## Contributing

1. Fork the repo.
2. Create a branch (`git checkout -b feature/xyz`).
3. Commit changes (`git commit -m "Add XYZ"').
4. Push (`git push origin feature/xyz`).
5. Open a Pull Request.

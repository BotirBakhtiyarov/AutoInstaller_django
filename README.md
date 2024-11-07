# AutoInstaller

AutoInstaller is a web application built with Django that facilitates the management and installation of software applications. It serves as a platform for users to view, install, and manage various applications directly from the server without the need for local installation files.

## Features

- **User-Friendly Interface**: Intuitive and responsive design for easy navigation and interaction.
- **Admin Panel**: Allows administrators to manage application details, user credentials, and oversee application installations.
- **Database Integration**: Utilizes PostgreSQL for robust data management and storage.
- **Application Management**: Users can browse a list of available applications, view details, and initiate installations directly from the web interface.
- **File Handling**: Supports uploading zip files containing application installers and scripts, which can be processed and installed seamlessly.

## Tech Stack

- **Backend**: Django
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Hosting**: Deployed on a cloud server for accessibility and reliability.

## Getting Started

### Prerequisites

- Python 3.x
- Django
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BotirBakhtiyarov/AutoInstaller_django.git
   ```
2. Navigate to the project directory:
   ```bash
   cd AutoInstaller
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database and run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

1. Access the application at `http://127.0.0.1:8000/`.
2. Explore available applications and use the admin panel for management tasks.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or feature requests.





# NIRO - Cinematic Streaming Platform

NIRO is a modern streaming platform application designed to provide a cinematic experience. It supports movies, series, offline downloads, and a sleek user interface.

## Features

- **Cinematic UI**: Modern, dark-themed interface focused on content.
- **Movies & Series**: Support for organizing and playing both movies and TV shows.
- **Offline Downloads**: Download content to watch offline (using IndexedDB).
- **Profile Management**: Multiple user profiles with "Continue Watching" history.
- **Admin Dashboard**: Manage content, upload videos/images, and users.
- **Cross-Platform**: Web application with a Windows desktop client wrapper.

## Project Structure

- `server.py`: Flask backend server (handles API and file serving).
- `index.html`: Main frontend application (Single Page Application).
- `app.js`: Core frontend logic (State management, Routing, IndexedDB).
- `styles.css`: Application styling.
- `launcher.py`: Python script to launch the application (or open the web version).

## Setup & Installation

### Prerequisites
- Python 3.x
- Pip

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server (Linux/Web Host)

To run the backend server:

```bash
python server.py
```

The application will be available at `http://localhost:8001` (or your server's IP).

### Desktop App (Windows)

The `NIRO_App.exe` is a lightweight launcher that opens the web application in a standalone window (Chrome/Edge App Mode).

To build the executable yourself:
```bash
pip install pyinstaller
pyinstaller NIRO_App.spec
```

## Deployment

The project is configured to run on `https://niro-tv.online`. The Windows executable acts as a shortcut to this URL.

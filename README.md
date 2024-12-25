# Job Posting Search Engine

This project is a job postings application that allows users to add new job postings and search for existing ones. It consists of a frontend built with React and Vite, and a backend built with FastAPI.


## Features

- **Job Postings Search**: Allows users to search for job postings based on keywords. Results are ranked by relevance.
- **Job Postings Upload**: Upload job postings in CSV format. The backend processes and stores them for searching.
- **Lexicon & Index Generation**: Automatically generates a lexicon and both forward and inverted indexes to speed up the search process.
- **Ranking System**: Job postings are ranked according to their relevance based on the user’s search query.
- **Dark Mode**: A toggle to switch between light and dark modes in the UI for user convenience.

## Installation

### Prerequisites

- Python 3.7+
- Node.js (for frontend)
- TailwindCSS (for styling)
- Shad Cn
- FastAPI (for backend)
- Vite (for frontend build)

### Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/anas464092/search-engine.git
   cd search-engine
   ```

2. **Frontend Setup (React + Vite)**
    Navigate to the client directory and install dependencies:

    ```bash
    cd client
    npm install
    ```
    Run the frontend on local host
    ```bash
    npm run dev
    ```

    This will start the development server for the frontend at http://localhost:5173.

3. **Backend:**

    ```bash
    cd server
    python -m uvicorn main:app --reload
    ```
    This will start the FastAPI backend server at http://localhost:8000.


## Demo

![Home Page](https://res.cloudinary.com/dl0xxcavw/image/upload/v1735138550/Screenshot_2024-12-25_195324_e5muvo.png)

![Add Document](https://res.cloudinary.com/dl0xxcavw/image/upload/v1735138691/Screenshot_2024-12-25_195756_rrgvco.png)

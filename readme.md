# AI Product Description Generator

## Description

This web application, built with FastAPI, automates the generation of product descriptions, SEO titles, and meta descriptions using the OpenAI API (specifically GPT-4o-mini). It's designed to process Shopify product CSV exports, allowing users to enhance their product listings efficiently. Users can upload CSVs, configure AI generation parameters (like prompt style, creativity, and length), process products, and download the updated CSV with AI-generated content merged back into the original format.

## Features

* **User Authentication:** Secure user registration and login system.
* **CSV Upload:** Supports uploading standard Shopify product export CSV files.
* **CSV Parsing & Validation:** Extracts product data (Handle, Title, Body, Image Src, SEO fields) and validates necessary columns. Skips variant rows automatically.
* **AI Configuration:**
    * Select AI model (GPT-4o-mini).
    * Adjust Temperature (creativity).
    * Set Max Tokens (output length).
    * Choose predefined prompt types (Conversion, Storytelling, Technical, LongTail SEO).
    * Option to include product images (processed to Base64) in the AI prompt.
* **AI Content Generation:** Interacts with OpenAI API to generate:
    * Product Descriptions (Body HTML)
    * SEO Titles
    * SEO Meta Descriptions
* **Content Processing:** Parses AI JSON responses and converts generated markdown to HTML/plain text.
* **Database Storage:** Uses SQLAlchemy with an async SQLite database to store user data, settings, uploaded file info, and product data.
* **Dashboard:** Central interface to:
    * Upload CSV files.
    * View recent uploads and their status.
    * Configure AI settings.
    * Initiate the AI generation process for pending products.
    * Download processed CSV files.
    * Clear user-specific data (uploads and products).
* **CSV Download:** Generates a downloadable CSV file containing the original product data merged with the newly generated AI content.
* **API Documentation:** Automatic API docs via Swagger UI (`/docs`) and ReDoc (`/redoc`).

## Technology Stack

* **Backend Framework:** FastAPI
* **Database:** SQLAlchemy (async) with SQLite (aiosqlite)
* **Authentication:** FastAPI Users, HTTP Basic Auth
* **AI:** OpenAI API (GPT-4o-mini)
* **Data Handling:** Pandas
* **Templating:** Jinja2
* **Frontend:** Basic HTML, CSS
* **Async:** `asyncio`, `httpx`

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ai_product_descriptions
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    Create a `.env` file in the project root directory (`2025.02.06__ai_product_descriptions`) and add the following variables:
    ```dotenv
    # .env
    DATABASE_URL="sqlite+aiosqlite:///./app_data.db" # Or your preferred async DB URL
    SECRET_KEY="your-very-secret-and-strong-key"    # Change this to a random secret key
    OPENAI_API_KEY="sk-..."                         # Your OpenAI API Key
    DEBUG=True                                      # Set to False in production
    ```
    * Replace `"your-very-secret-and-strong-key"` with a securely generated secret key.
    * Replace `"sk-..."` with your actual OpenAI API key.

## Running the Application

1.  **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    * The `--reload` flag enables auto-reloading during development. Remove it for production.
2.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000`. You will be redirected to the login page.

## Usage

1.  **Register:** Create a new user account via the `/register` page.
2.  **Login:** Log in using your credentials via the `/login` page.
3.  **Configure Settings:** Navigate to the `/settings` page (link available on the dashboard) to configure the AI model, temperature, prompt type, etc. Save your settings.
4.  **Upload CSV:** On the dashboard (`/dashboard`), upload your Shopify product CSV file.
5.  **Process Products:** Click the "Start AI Products Description Generation" button on the dashboard. The application will process pending products using your saved settings.
6.  **Download Results:** Once processing is complete, find the corresponding file in the "Recent Uploads" or "Download Processed Products CSV" section and click "Download". This will provide a CSV file with the AI-generated content merged in.

## API Endpoints

* **Web Interface:**
    * `/`: Redirects to `/login`.
    * `/login`: User login page.
    * `/register`: User registration page.
    * `/dashboard`: Main user dashboard.
    * `/settings`: AI configuration page.
    * `/logout`: Logs the user out.
* **API Actions:**
    * `/upload-csv`: Handles CSV file uploads (POST).
    * `/process-products`: Triggers AI generation for pending products (POST).
    * `/download/products_output/{uploaded_file_id}.csv`: Downloads the processed CSV (GET).
    * `/clear-data`: Clears user's uploaded files and product data (POST).
* **API Documentation:**
    * `/docs`: Swagger UI.
    * `/redoc`: ReDoc documentation.

## Folder Structure

```
2025.02.06__ai_product_descriptions/
├── app/                    # Main application package
│   ├── models/             # SQLAlchemy models (User, Product, Settings, etc.)
│   ├── routes/             # API route definitions (auth, dashboard, upload, etc.)
│   ├── services/           # Business logic (CSV parsing, AI interaction, prompts, etc.)
│   │   └── prompts/        # JSON files defining AI prompts
│   ├── __init__.py
│   ├── auth.py             # Authentication logic
│   ├── config.py           # Application settings (from .env)
│   ├── db.py               # Database setup and session management
│   ├── main.py             # FastAPI app initialization and middleware
│   └── users.py            # User management schemas and logic
├── static/                 # Static files (CSS)
├── templates/              # Jinja2 HTML templates
├── .env                    # Environment variables (Needs to be created)
├── requirements.txt        # Python dependencies
├── readme.md               # This file
└── ...                     # Other config/test files (pytest.ini, etc.)
```

## Notes

* The application expects a CSV file formatted like a standard Shopify product export. Key columns used are: `Handle`, `Title`, `Body (HTML)`, `Image Src`, `SEO Title`, `SEO Description`.
* Ensure your OpenAI API key has sufficient credits/quota.
* The default database is SQLite (`app_data.db` created in the root if using the default `.env` setting). 

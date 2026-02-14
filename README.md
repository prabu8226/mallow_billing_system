
## 🚀 Getting Started

### 1. Prerequisites
- **Python**: 3.12+
- **Database**: PSQL (default)

### 2. Installation

Clone the repository and navigate to the project root:

```bash
cd mallow_billing_system
```

Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration ⚙️

The application uses environment variables for security. Create a `.env` file in the project root:

```ini
# Security
SECRET_KEY=your-secret-key-here

# Email (SendGrid Configuration)
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=Your Name <your-email@example.com>
```

### 4. Database Setup

Apply migrations and seed initial product data:
```bash
setup pssql configuration
python manage.py migrate
python manage.py seed_products
```
*Note: `seed_products` will populate the database with a catalog of items to get you started immediately.*

### 5. Running the App

Start the development server:
```bash
python manage.py runserver
```
Visit the app at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

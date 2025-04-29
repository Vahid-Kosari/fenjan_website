# Fenjan Project

The main idea behind this application comes from a similar Flask-based project using MySQL by [mh-salari](https://github.com/mh-salari).

This project has been redeveloped using Django and JavaScript to handle both backend functionality and the web interface.

---

## Distinctiveness and Complexity

**Fenjan** (meaning *cup* in Persian) symbolizes the essence of this project: providing users with a personalized experience while they enjoy a cup of their favorite drink. The Fenjan project allows users to submit keywords and their email address to initiate a web scraping process (currently focused on LinkedIn), organize the results in a structured format, and receive them directly via email.

Users are offered a free three-day trial period, during which they can receive job results by email. After the trial, they can request registration under custom conditions to gain full access, including regular email reports and a personalized user panel.

---

### 🔐 Security Measures and Selenium Management

The credentials for accessing LinkedIn and the email service are stored securely in a local `.env` file. I learned how to work with `.env` files to prevent credential exposure in the source code. For browser automation with Selenium and integration with LinkedIn, I configured a custom agent for login persistence and tuned browser options for compatibility with LinkedIn's structure.

---

### ⚙️ Backend Infrastructure

To manage user access and schedule tasks, Redis and Celery are used. (For Windows, Ubuntu-like support can be simulated via appropriate apps.) The configurations are defined in `settings.py`, and supporting logic resides in `signal.py`, `tasks.py`, and `capstone/celery.py`. Additional configurations are placed in the `capstone/celery_conf` folder and `capstone/celerybeat-schedule`. Settings can be modified via the Django admin panel as well.

User data is stored in `models.py` under the `Customer` and `LinkedInSearchResult` models. The admin panel is enhanced slightly to provide insight into user status.

> Files `linkedin_sgai.py` and `llama3.py` are obsolete.

---

### 🔍 Data Extraction and Processing

Initially, I experimented with ASGI modules and the Llama3 model for scraping and data formatting. However, the results were unsatisfactory, so I manually analyzed LinkedIn's site structure to better extract relevant data. This manual process required significant time and effort.

The main function, `find_positions()`, is responsible for surfing job listings and returning results in HTML, JSON, and list formats. These are then used for email delivery and displaying filtered, well-structured results on the web.

To assist with development monitoring, the `tqdm` library is used to visualize progress through the pages and keywords. The algorithm ensures similar or irrelevant posts are filtered out.

Under the hood, `filter_positions()` refines results, and `extract_positions_parts()`—leveraging BeautifulSoup—parses HTML, removes non-English content, filters hashtags, cleans excess content, and structures the final output. This step was particularly challenging and required precise HTML element targeting.

All results are stored in the database for both web viewing and email delivery.

---

### 📧 Email Delivery

The prepared HTML results are sent using Python’s `smtplib` and `EmailMessage`. The `compose_and_send_email()` function handles the delivery, generating well-structured HTML emails from user data and the scraped results. The email body is composed using the `compose_email()` function in `compose_email.py`. Image resources are made accessible via Nginx on an Ubuntu VPS.

---

### ⚙️ VPS Deployment and Services

This project (along with others developed during the CS50W program) is hosted on my website under the [rahrow.ca](https://www.rahrow.ca) domain. I personally managed the entire deployment—setting up the VPS, Nginx, Gunicorn, domain hosting, and Cloudflare—without using third-party deployment platforms.

---

### 🎨 User Interface and Design

The user interface is designed for both desktop and mobile users. AI-generated images enhance visual appeal, and Figma was used for layout design. An image map on the main page allows form submission via a hot chocolate cup graphic, while admin access is subtly embedded in the hand of the purple-green dinosaur mascot.

This feature is intentionally hidden from non-admin users. The UI follows a minimalist approach, using JavaScript only when necessary.

---

## 🚀 How to Run the Fenjan Project

### 1. (Optional) Create a Virtual Environment

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv myenv
source myenv/bin/activate
```

**OR using Conda:**

```bash
sudo apt update
sudo apt install miniconda
conda create -n myenv python=3.x
conda activate myenv
```

---

### 2. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

---

### 3. Install Dependencies

Make `setup.sh` executable and run it:

```bash
chmod +x setup.sh
./setup.sh
```

If it fails, install system packages required for Playwright:

```bash
sudo apt-get update
sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
```

Then install Python dependencies:

```bash
pip install -r requirements.txt
```

---

### 4. (Optional) Initialize a Fresh Database

```bash
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

---

### 6. Set Up Supervisor for Celery Tasks

6.a. Place the config files from `capstone/celery_conf` into:

```bash
/etc/supervisor/conf.d/
```

6.b. Reload Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
```

6.c. Start the services:

```bash
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

6.d. Alternatively, run the workers manually for development:

```bash
celery -A capstone worker --loglevel=info
celery -A capstone beat --loglevel=info
```

---

### 7. Run the Development Server

```bash
python manage.py runserver
```

---

### 8. Access the Application

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or your deployed domain.
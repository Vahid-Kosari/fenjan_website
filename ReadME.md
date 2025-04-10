# Fenjan Project

The main idea of this application comes from a similar Flask-driven application in conjunction with MySQL by [mh-salari](https://github.com/mh-salari).

This project has been renovated using Django and JavaScript to create this web application back-end and interface.

# Distinctiveness and Complexity

Fenjan (meaning "cup" in Persian) symbolizes the essence of this project: offering users a personalized experience while they enjoy a cup of their favorite drink. The Fenjan project allows users to provide their keywords and email address to initiate a web scraping process (currently focused on LinkedIn), organize the results in a structured format, and send the relevant findings directly to their email.

To achieve this, users are offered a free trial period of three days, during which they can receive results via email. After the trial, users can request registration under preferred conditions to gain full access, including emailed reports and a personalized user panel for a specified duration.

### Security Measures

The credentials for accessing LinkedIn's API and the email service used for sending results are securely stored in a local `.env` file to prevent exposure through the source code.

### Backend Infrastructure

To manage user access and ensure timely updates, Redis and Celery are utilized for task scheduling and background job management (for windows, ubumtu should be simulated by apps to support). These tools help keep the application scalable and responsive. Users' data is stored in the models.py as Customer and LinkedInSearchResult classes. Also, admin interface enhanced a little to inform the admin about users' state. linkedin_sgai.py and llama3.py are obsolete.

### Data Extraction and Processing

Initially, I experimented with ASGI modules and the Llama3 model to format the scraped data. However, due to unsatisfactory results, I conducted an in-depth analysis of LinkedIn's site structure. This manual process took significant time and effort to understand the layout and extract relevant, structured data. The focus is on identifying posts with application links and repackaging the extracted content into a readable, user-friendly HTML format.

### Email Delivery

The prepared HTML reports are sent to users via email using Python's `smtplib` and `EmailMessage` libraries, ensuring a seamless delivery process.

### User Interface and Design

The website's appearance is crafted with attention to both desktop and mobile versions. AI-generated images enhance the visual appeal, while Figma was used to design the layout for an optimal user experience across different devices.
As the interface is designed minimally, employing JavaScript was not the case and not used more than enough.

## How to Run the Fenjan Project

Follow these steps to set up and run the Fenjan project:

1.  **(Optional) Create a Fresh Environment**

    - It's recommended to create a virtual environment to isolate dependencies.
      ```sudo apt update
      sudo apt install python3-venv
      python3 -m venv myenv
      source myenv/bin/activate
      ```
      OR
      ```sudo apt update
      sudo apt install miniconda
      conda create -n myenv python=3.x
      conda activate myenv
      ```

2.  **Download the Repository**

    - Clone the repository to your local machine:
      ```sh
      git clone <repository-url>
      cd <repository-directory>
      ```

3.  **Install the Required Packages**

    - Install dependencies all together (preferred):
      Make `setup.sh` executable, and then run it:

    ```sh
    chmod +x setup.sh
    ./setup.sh
    ```

    - If you want to install manually or the above did not work, install system dependencies for playwright manually:

      ```sh
      sudo apt-get update
      sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
      ```

    - Install the dependencies listed in `requirements.txt`:
      ```sh
      pip install -r requirements.txt
      ```

4.  **(Optional) Initialize a Fresh Database**

    - To start with a fresh database, delete `db.sqlite3` and run the following commands:
      ```sh
      python manage.py makemigrations
      python manage.py migrate
      ```

5.  **Create a Superuser for Administration**

    - To create an admin user, run:
      ```sh
      python manage.py createsuperuser
      ```

6.  **Set Up Supervisor for Automated User Registration State's Supervision**

    - Configure Supervisor to manage Celery worker and beat processes:

      6.a. Adopt and customize the configuration files for Celery worker and beat from `capston/celery_conf` for your environment. Place them in the following directory:

      ```sh
      /etc/supervisor/conf.d/
      ```

      6.b. Update Supervisor to apply the new configurations:

      ```sh
      sudo supervisorctl reread
      sudo supervisorctl update
      ```

      6.c. Start the Celery services:

      ```sh
      sudo supervisorctl start celery_worker
      sudo supervisorctl start celery_beat
      ```

      6.d. Run the Celery worker and beat scheduler in two terminals from project location (This step, only, should be performed every time that celery should become active or restart):

      ```sh
      celery -A capstone worker --loglevel=info
      celery -A capstone beat --loglevel=info
      ```

7.  **Run the Project**

    - In the root directory of the project, start the development server:
      ```sh
      python manage.py runserver
      ```

8.  **Open the Application in Your Browser**
    - Navigate to the dedicated URL (typically `http://127.0.0.1:8000/`) to access the application.

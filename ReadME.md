# Fenjan Project

The main idea of this application comes from a similar Flask-driven application in conjunction with MySQL by [mh-salari](https://github.com/mh-salari).

This project has been renovated using Django and JavaScript to create this web application interface.

## How to Run the Fenjan Project

Follow these steps to set up and run the Fenjan project:

1. **(Optional) Create a Fresh Environment**

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

2. **Download the Repository**

   - Clone the repository to your local machine:
     ```sh
     git clone <repository-url>
     cd <repository-directory>
     ```

3. **Install the Required Packages**

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

4. **(Optional) Initialize a Fresh Database**

   - To start with a fresh database, delete `db.sqlite3` and run the following commands:
     ```sh
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Create a Superuser for Administration**

   - To create an admin user, run:
     ```sh
     python manage.py createsuperuser
     ```

6. **Set Up Supervisor for Automated User Registration State's Supervision**

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

7. **Run the Project**

   - In the root directory of the project, start the development server:
     ```sh
     python manage.py runserver
     ```

8. **Open the Application in Your Browser**
   - Navigate to the dedicated URL (typically `http://127.0.0.1:8000/`) to access the application.

---

include a writeup describing your project, and
specifically your file MUST include all of the following:
Under its own header within the README called Distinctiveness and Complexity:
Why you believe your project satisfies the distinctiveness and complexity requirements, mentioned above.
What’s contained in each file you created.
How to run your application.
Any other additional information the staff should know about your project.

=>
writing a README.md that you are proud of and that documents your project thoroughly, and that distinguishes this project from others in the course and defends its complexity.

Simply saying, effectively, “It’s different from the other projects and it was complex to build.” is not at all sufficient justification of distinctiveness and complexity.

This section alone should consist of several paragraphs, before you even begin to talk about the documentation of your project.

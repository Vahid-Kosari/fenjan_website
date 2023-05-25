This is a web app created by vahid-kosari under supervision of hue-salari that assist you in finding your dream Ph.D. position.
To run the application go to the project root and run the "fenjan.py" app under Flask framework by following commands:

1-activate appropriate environment "fenjan" by: conda activate fenjan

2-setup environmets variables for Flask as:
    export FLASK_APP=fenjan.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1 (NOT necessary because we added this:     app.run(debug=True))

3-run the app by: flask run

You must receive somthing like this:
* Serving Flask app 'fenjan.py'
* Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
* Restarting with stat
* Debugger is active!
* Debugger PIN: 239-541-107

4-Follow the http://127.0.0.1:5000 by ctrl + click

Enjoy
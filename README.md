Workbook Exporter

Workbook Exporter is a Flask web application that processes CSV files, runs specified exporters on them, and generates output files based on the selected exporters. It also allows users to provide an existing YAML configuration file for processing.
Features

    Upload CSV and optional YAML files
    Select from a list of available exporters
    Process the uploaded files with the chosen exporters
    Display progress in a live-updating terminal window
    Clean up temporary files and download the output

Prerequisites

    Python 3.7+
    Flask
    Werkzeug

Installation

    Clone the repository:

    bash

git clone https://github.com/Brownster/workbook_exporter.git

Change to the project directory:

bash

cd workbook_exporter

Install the required packages:

    pip install -r requirements.txt

Usage

    Run the Flask app:

to run gunicorn -w 4 -b 0.0.0.0:8000 workbook_exporter-fe5:app

    arduino

export FLASK_APP=app.py
export FLASK_ENV=development
flask run

On Windows, replace export with set:

arduino

    set FLASK_APP=app.py
    set FLASK_ENV=development
    flask run

    Open your browser and navigate to http://127.0.0.1:5000.

    Upload a CSV file and, optionally, a YAML configuration file.

    Choose the desired exporters from the list.

    Click the "Process" button to run the selected exporters on the uploaded files.

    Monitor the progress in the terminal window.

    Once the processing is complete, click the "Finish and Clean" button to clean up temporary files and return to the initial file upload screen.

Customizing Exporters

You can add or modify exporters in the app.py file. To add a new exporter, define a function for the exporter, then include it in the list of available exporters in the process_file function.
Contributing

If you want to contribute to this project, please submit a pull request with your changes. We welcome any contributions, whether it's fixing bugs, adding new features, or updating documentation.



![Screenshot from 2023-04-16 10-39-13](https://user-images.githubusercontent.com/6543166/232290330-8da3571e-e06a-4e51-8b01-8773ab11c2d0.png)


![Screenshot from 2023-04-16 10-39-38](https://user-images.githubusercontent.com/6543166/232290325-768edd3a-5caf-4f71-b561-24b8b7eebdaf.png)

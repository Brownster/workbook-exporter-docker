Workbook Exporter

Workbook Exporter is a Dockerized Flask web application that processes CSV and Excel workbook files, allowing users to apply specified prometheus exporters and generate output yaml config files based on their selections. It supports the use of YAML existing configuration files uploaded along side excel / csv doc these targets will be added to existing yaml config.


    Upload CSV or Excel and optional YAML configuration files.
    Select from a list of available exporters.
    Process the uploaded files with the chosen exporters.
    Display processing progress in a live-updating terminal window.
    Clean up temporary files and allow users to download the output.

Prerequisites

    Docker

Installation & Running with Docker

Instead of setting up a Python environment manually, you can use Docker to run the application. This ensures that the application runs consistently across all environments.
Pull the Docker Image

You can pull the latest version of the Workbook Exporter from Docker Hub:


docker pull brownster/workbook-exporter:latest

Run the Container

To run the application:


docker run -d -p 5000:5000 --name workbook-exporter yourusername/workbook-exporter:latest

This command starts the workbook-exporter container and makes it accessible via http://localhost:5000.
Usage

    Open your browser and navigate to http://localhost:8000.
    Upload a CSV or Excel file and, optionally, a YAML configuration file that will be updated.
    Choose the desired exporters from the list provided.
    Click the "Process" button to start the processing of the uploaded files.
    Monitor the processing progress through the terminal window integrated into the web interface.
    Downloading of the processed output yaml is automatic.
    Once processing is complete, click the "Finish and Clean" button. This will clean up any temporary files.
    
Customizing Exporters

To customize or add new exporters:

    Dockerized App Modification: If you wish to add or modify the existing exporters, you will need to make changes to the application code. Clone the repository, make your changes, and rebuild the Docker image.

    bash

    git clone https://github.com/Brownster/workbook_exporter.git
    cd workbook_exporter
    # Make your changes
    docker build -t brownster/workbook-exporter:latest .

    Update the Application: After changes, push the new version of the Docker image to Docker Hub, and redeploy the container.

Contributing

We welcome contributions from the community, whether they are bug fixes, improvements, or new features. Please fork the repository and submit a pull request with your updates.
Screenshots

Here are some screenshots of the application:
![image](https://github.com/Brownster/workbook-exporter-docker/assets/6543166/f6cec27d-098e-4d49-8d58-04fcb1acb7ed)
![image(1)](https://github.com/Brownster/workbook-exporter-docker/assets/6543166/552ff1d4-a089-476c-ba8c-2c2561970754)




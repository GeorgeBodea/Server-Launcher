# Server Launcher

Server Launcher is a Flask-based web application that simplifies the process of launching AWS EC2 instances pre-configured with development tools like Python, MySQL, and game servers. This project leverages Python, Flask, Boto3, Jinja2, and Bootstrap for rapid and efficient cloud deployment.

## Features
- Launch EC2 instances with predefined configurations
- Choose tool versions and AMI types
- Manage AWS instances (start, stop, terminate)
- View instance details and download SSH private keys

## Technologies Used
- **Python** (Flask, Boto3)
- **Flask Extensions** (Flask-Login, Flask-SQLAlchemy)
- **Jinja2** for HTML templating
- **Bootstrap** for front-end design
- **AWS EC2** for server hosting

## Prerequisites
Before running the application, ensure the following are installed:
- Python 3.x
- AWS CLI with local configuration (`aws configure`)
- Virtual environment setup (`venv`)

## Configurations

1) Install and configure AWS CLI locally, using your AWS account:
   
If not installed, download and install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

Afterwards, create the configuration and credential files using this command:

```bash
aws configure
```

Follow the prompts to set up your AWS access keys and default region. This will allow the application to interact with AWS EC2.


2) Installation and Setup of the actual project

Clone the repository:

```bash
git clone https://github.com/GeorgeBodea/server-launcher.git
cd server-launcher
```

3) Create a Python virtual environment:

```bash
python3 -m venv env
source env\Scripts\activate # On Linux or macOS: env/bin/activate
```

4) Install the required dependencies:
   
```bash
pip install -r requirements.txt
```

## Running the application:

1) Start the Flask application:
   
```bash
python main.py
```

2) Access the webpage:
   
The application will be available at:

```bash
http://0.0.0.0:5000
```

## Usage
- Log in or register a new account.
- Select the AMI type and instance type for the AWS EC2 instance.
- Choose the development tools (e.g., Python, MySQL) to be installed on the instance.
- Launch and manage the server via the web interface.




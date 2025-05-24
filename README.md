# Knowledge Learning Project

Welcome to Knowledge Learning, a platform dedicated to online training courses.

## Table of contents

   - [Description] (#description)
   - [Main features](#main-features)
   - [Project architecture](#project-architecture)
   - [Installation](#installation)
   - [Deployment Setup](#deployment-setup)
   - [Contributors](#contributors)

### Description

Knowledge Learning Project is an e-learning platform developed with Django.
It allows users to sign up, activate their account via email, purchase full curricula and individual lessons, track their progress, complete lessons, and earn certifications.
An admin back office is also available for managing content and users.

### Main features

   - **User Management** : registration, email activation, and login via email only.
   - **E-learning Catalog** : purchase of full curricula or individual lessons.
   - **Progress Tracking** : lesson completion with detailed tracking.
   - **Certification** : issuance of certificates upon curriculum completion.
   - **Integrated Payments** : Stripe for secure transactions.
   - **User Dashboard** : display of purchased curricula and lessons with their status.
   - **Admin Backoffice** : full management of users, content, and payments.

### Project architecture

The Django project is organized into several applications (apps):

| App                 | Main role                                                |
|---------------------|----------------------------------------------------------|
|`users`              | Custom user management                                   |
|`courses`            | Management of themes, curriculums and lessons            |                         
|`cart`               | Cart management                                          |
|`payments`           | Managing payments with Stripe                            |
|`dashboard`          | Displaying the user dashboard                            |
|`certificates`       | Certification management                                 |
|`core`               | Shared core features                                     |

### Installation

#### Prerequisites

   - VSCode or PyCharm
   - Python
   - Pip
   - Django

#### Installation

   1. Clone the repository : git clone https://github.com/Nathi33/knowledge_learning_project.git
   2. Navigate to the project directory : cd knowledge-learning-project
   3. Create and activate a virtual environment:
        ```bash
        python -m venv env 
        env\Scripts\activate # Windows
        source env/bin/activate # Linux / MacOS
   4. Install dependencies : pip install -r requirements.txt
   5. Configure the database (SQLite by default) : python manage.py migrate
   6. Launch the server : .\start.ps1
   7. The application will be accessible at http://localhost:8000

### Deployment Setup

   - To build the project for deployment, use the commands : 
        ```bash
        python manage.py collectstatic --noinput
        python manage.py migrate
   - Run unit tests with Pytest : pytest

### Contributors

   - Nathi33 - Lead developer
   - Contributions and suggestions are welcome via pull requests


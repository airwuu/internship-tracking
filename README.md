# internship-tracking

mostly vibecoded app for personal use. I wanted to run something locally instead of using some service by someone else. 

will polish when I have more time, installation instructions down below if you want

<img width="762" height="759" alt="image" src="https://github.com/user-attachments/assets/639b342d-edea-4fb2-9b3a-4c32cbc4c399" />

## Features

-   **Add, Edit, & Delete:** Easily manage your job applications.
-   **Status Tracking:** Update the stage of each application from "Applied" to "Offer".
-   **Sankey Diagram:** Automatically generates Sankey diagram to reflect your job hunt
-   **Search & Filter:** Quickly find applications by company, role, or status so you can update it fast
-   **Personal Links:** Easily copy your personal links that you need for job applications
## Prerequisites

-   Git
-   Python 3

## Getting Started

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

First, clone the project to your local machine using Git.

```bash
git clone [https://github.com/airwuu/internship-tracking.git](https://github.com/airwuu/internship-tracking.git)
cd internship-tracking
```
### 2. Connect to a database (supabase)
We want to connect a database, we can use supabase free plan for this. Sign up for supabase, in your project look for the "connect" button and get a URI or session pooler link and paste it into the `.env`
```bash
cp example.env .env
```
### 3. Run project
everytime you want to run the project, run `./start.sh` in your terminal and follow the link to the website. 
```bash
./start.sh
```

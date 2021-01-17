# Shopify Intern Challenge Summer 2021
Built this project for the back end developer role at Shopify. See the link below

https://docs.google.com/document/d/1ZKRywXQLZWOqVOHC4JkF3LqdpO3Llpfk_CkZPR8bjak/edit

This project focused on creating a web application similar to instagram (but much simpler haha) that can: 
    -register and login users
    -add image(s)
    -view images based on privacy level of an image and the current session.

The project was built using flask because I was most comfortable with Python and wanted to learn how to use flask. Django seemed to have a higher learning curve not suitable for a time sensitive project.

# Installation and usage
This project will need Python3 installed.

You should create a virtual environment for this project. 
Open a cmd (or terminal) and change directories to the top level of this project. Then:
`py -3 -m venv env`
`.\env\Scripts\activate`
To deactivate later use `deactivate` whilst in the same directory.
`pip install -e .`
`SET FLASK_APP=flaskr` This will be different if you use macOS or Linux, I developed this project on a windows 10 machine

Once you have installed the application then initialize the database
`flask init-db`
Then run the server
`flask run`
Go to `http://127.0.0.1:5000/`


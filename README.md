**Project Overview and Purpose**

This is a small personal project made for the purposes of the CS50 Introduction to Computer Science course on EdX.org.

It is a small website with blog posts as the central focal point. You are able to create users, follow and friend users, send message, post a status and update certain aspects of your personal user profile.

Obviously you can also create blogs, view bogs, and edit blogs you created.

The website's backend is based on Python and the Flask framework. Utilising many plugins for the framework, such as Flask-SQLAlchemy to handle database requirements, to flesh out the funtionality of the application.

The application uses an application factory to create the application and the application contexts. The HTML templates are made with Jinja2 templating as a key integral part for dynamic webpages.


**Requirements and Setting Up the Project**

This project comes with a requirements.txt file that you can use to install all dependencies via pip.

This project uses Flask-SQLAlchemy for it's database and ORM. When creating a new application without an existing database use the following line to set up the database in an interactive python shell:

from app import db

db.create_all()

The application also uses Flask-Migrate to handle updates to the database and tracking the changes made. To create the initial migration folder (needed to use this extension) execute the following from a command line:

flask db init

You can then crate migration files and update your active database with the following commands from the command line:

flask db migrate -m "Place a message here shortly describing what updates have been made"

flask db update

Once that is set up you will need to set the environment variable FLASK_APP in the command line to blog.py. If you wish to have access to the live debugger offered by the application also set FLASK_ENV to development.

Once those are set you can run the built-in web server with the following command from the command line:

pyton -m flask run

There was a bug with the version of Flask this was built on, where running 'flask run' issued an error. This could have been corrected in the code for the Flask library but did not want to play around with it myself.

Do keep in mind that this built-in web server is not for production, but rather to test and play around during development. Set up a proper web server service for deployment of any application made.


**What You Can Do With This Project**

This was, as stated above, created not as a commercially viable application, but rather as a project for a course being taken for me to learn from. 

But if you find value here you are more than welcome to take it, play around with it, and learn from it as well. I used many different ideas and techniques in the learning process,many that may not always be advisably used together, but perhaps you can find some value in looking through it.

If you wish to suggest better methods or corrections then I am always open to it. My ego is capable of taking criticism and constructive suggestions. Including on the, quite surely, lackluster readme here!


**Possible To-Do's for the project**

I have many things on my mind that I wanted to implement with this project, out of interest, but decided against because of the time it would take to implement them all! And this project has already taken quite some time, and all things must come to an end eventually.

I may revisit this project in the future to play around again and implement the features I wanted to now, some of which I will list below for prosperity:

- Live search features; perhaps to look up users by name, or blogs by title and content. 
- Translation features; to allow users from all over the globe to communicate somewhat easily with each other without needing to speak the same language.
- Implement more dynamic and responsive web design concepts; I played around with it a bit and started some parts of responsive design within the CSS file, but did not have the time to really dedicate to fleshing it out like it should be.
- Have live notifications; for when followed/friend users post statuses, blogs, or you receive a message. There is a semi-live notification setup for messages when they arrive. But it only updates as the webpage is refreshed, rather than as the message is received.
- Allow users to choose and update their user profile pictures; Right now I utilise a service to automatically assign avatars to all users. I would like to play around with implementing functionality for users to upload their own images for their profile.
- Allow users to create more interesting blogs; along the same line of thought, right now the blogs are simply text presented on a screen in a simple format. I'd like to have users able to create much more interesting blogs, with different fonts, formats and inclusion of pictures.
- Finish implementing tests for application; I have a number of tests done, but there are a fair number still outstanding completion.
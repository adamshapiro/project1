# Project 1

### Web Programming with Python and JavaScript

This Website allows visitors to log in or sign up accounts so that they can view
detailed information for various locations throughout the US, as well as check in
to each location with a personalized message.
The following files are used:

### HTML
---
* [layout.html](/templates/layout.html): The basic layout extended by each other html page.
    Includes a navbar for logging out and returning to the search page.

* [index.html](/templates/index.html): The search page. Users can search by zip code, city, or state.
    The results will then be displayed in a table below the search form, with an option
    to view more details for any location.

* [location.html](/templates/location.html): A page used for displaying more details about
    a given location. These details include latitude and longitude, population, as well
    as current weather information taken from the DarkSky API. This page also allows a user
    to check in to the location with an optional message, and shows the number of check ins
    and messages already left.

* [login.html](/templates/login.html): The login and sign up page. The same page is used
    for both login and signup, and users can alternate between the two. Users must be logged in
    before visiting the search or location pages.

### Python
---
* [application.py](/application.py): The main file for running the flask server. Controls
    routing for each HTMl page, as well as an API route for getting a small amount of information
    for a location via its zip code.

* [models.py](/models.py): A file containing ORM information for the database tables:
    * **Location**
    * **User**
    * **Check_In** (used for mapping a location id and a user id to a message)

* [import.py](/import.py): A file for importing a csv of location information to
    to the appropriate database table.

### MISC
---
* [requirements.txt](/requirements.txt): A list of python modules that must be installed before
    running the application.

* [zips.csv](/zips.csv): The CSV file of locations imported into the database

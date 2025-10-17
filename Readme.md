#Fitbit OAuth Server app for GIMWearables project

This is a skeleton app to save authorization tokens for multiple devices and then expose the fitbit API (using python-fitbit) to grab data. 
It is written in Python 3.5 and based on code from https://github.com/Bachmann1234/FitbitFlaskTemplate

To install, clone this repo somewhere, and create a virtual environment (I am using conda):
```
# Create a virtual environment for 
conda create --name <yourenv> python==3.5 pip
conda activate <yourenv>
pip install -r requirements.txt
```
*Currently need git.exe installed to get a more recent copy of python-fitbit* can work on different library later

Then go to the [Fitbit App Config](https://dev.fitbit.com/apps/new), use Server mode with Callback URL http://localhost:5000/oauth-redirect. Note that the account must be approved for 'Intraday' data for non-personal devices in order to work like this in server mode.

Once you have that you need to define some environment variables. I am running Windows so I made the following batch script and included it as part of the conda environment activation script:

```
:: %CONDA_PREFIX%\etc\conda\activate.d\env_vars.bat
set FITBIT_CLIENT_ID=<your_client_id>
set FITBIT_CLIENT_SECRET=<your_secret_key>
set SECRET_KEY=sdasdas
set FLASK_CONFIG=development
```

Only development mode has been tested so far - works fine as a local application. 

After defining those you are ready to setup development.

The app stores usernames and tokens in an sqlite database. This is by no means secure and is not meant to be deployed to the web.

The OAuth scopes are defined in fitbit.py. This app requests all persmissions.

The first time you run the app you need to create the database. With your virtual environment activated run
```
python manage.py createdb
```

Finally to run the app simply make sure your virtual environment is active and run

```
python manage.py
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger pin code: 129-285-482
```

Authenticate users on the index page

http://localhost:5000

Access the data using an HTTP GET request (i.e. in the browser):
```
http://localhost:5000/data/<username>/intraday/activities-heart/2019-06-13/1sec
```
Where 'username' is either the email associated with the fitbit device, or the string 'all', which will cause a dump of data from all registered devices as a JSON dict. Only intraday activity for heartrate is currently setup.

The idea is to have this flask server running on a local machine as an authentication layer for multiple accounts, and then use a separate process to send a daily request and log the data. The list of authenticated users is available at http://localhost:5000/users



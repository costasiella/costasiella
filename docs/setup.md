# This guide assumes you'll install costasiella in the following directories:

backand: /opt/costasiella
frontend: /var/www/html/build
virtual environments: /opt/venvs

(Django root = /opt/costasiella/app)

# Install required packages

$ sudo apt install git python3-pip python3.6-dev libmysqlclient-dev nginx-full mysql-server-5.7 redis-server redis-tools

## 

# Fetch files

## 

cd /opt
git clone https://github.com/costasiella/costasiella.git 

## 

# Database setup

# (Please change the username and password to something more secure)

## 

sudo mysql
CREATE DATABASE costasiella CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
grant all privileges on costasiella.* to ‘user’@’localhost’ identified by ‘password’;
CREATE DATABASE vault CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
grant all privileges on vault.* to ‘user’@’localhost’ identified by ‘password’;
flush privileges;

## 

# Vault setup

## 

Download Vault from https://www.vaultproject.io

Create an empty file called vault_config_dev.hcl (or anything to your liking) and put the following in it:

ui = true
disable_mlock = true

storage "mysql" {
  username = "user"
  password = "password"
  database = "vault"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = true
}

Edit the storage section with your database information.

Start the Vault server using

vault server -config=/path/to/config/config_dev.hcl

Open a webbrowser and go to http://localhost:8200/ui to perform an initial setup for Vault.
For key shares and key threshold, fill in a 1. Plase note that for production something like 5 and 3 would be more appropriate.

!Important!
Save the root token and key somewhere safe. When these keys are lost, you lose all access to Vault and the encrypted data.

Continue by clicking the “Unseal” button and enter the key from the previous step (not the root token).
Then sign in to vault using the root token.

Set up the transit engine
Click “Enable new engine” and choose Transit under generic. Enter a recognizable name for the Path, in this document the default name “transit” will be used for the transit engine path. Click enable engine on the bottom of the page.

Click “Create encryption key” and enter a recognizable name. Then click the Create entryption key button. 
In this document “costasiella” will be used as the name for the encryption key.

In case you’d like to do further vault setup (at some point) using the terminal, add the following lines to the .bashrc file in your home directory.

# Vault config

complete -C /usr/local/bin/vault vault
export VAULT_ADDR=http://127.0.0.1:8200

## 

# Update settings

## 

cd opt/costasiella/app/app

Edit settings/common.py

    • Edit the databases section as required.
    • Under Vault configuration edit the following settings to reflect your environment.

VAULT_URL = ‘http://localhost:8200’
VAULT_TOKEN = <Your root token here, definitely bad idea for production, but fine for development or evaluation>
VAULT_TRANSIT_KEY = “costasiella”

## 

# Optional

# Globally setup virtualenv and virtualenvwraper for easier management of your virtual environments

## 

sudo pip3 install virtualenv virtualenvwrapper

Add the following to your .bashrc file(s) 

# virtualenvwrapper setup

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=/opt/venvs
export PROJECT_HOME=/opt
export VIRTUALENVWRAPPER_SCRIPT=/usr/local/bin/virtualenvwrapper.sh
source /usr/local/bin/virtualenvwrapper_lazy.sh

Create the virtualenvirontment

sudo mkvirtualenv -p /usr/bin/python3 costasiella

# In your Django root execute the command below to install the required python modules

pip3 install -r requirements.txt

# In your Django root execute the command below to create your database tables:

./manage.py migrate

# Load the setup data

./manage.py loaddata costasiella/fixtures/*.json

# Create a super user

./manage.py createsuperuser

> enter your information

## 

# Static files collection

## 

./manage.py collectstatic

## 

# TO DO

## 

- uwsgi setup
- nginx setup

## 

# Create user and log in

## 

Open a webbrowser (tab) and go to localhost:8000/admin. 
Log in using the admin credentials created above.

# Create group & assign group permissions

Click Home in the breadcrumb top left.
Under the AUTHENTICATION AND AUTHORIZATION SECTION click “Add” next to Groups.
Give the group a recognizable name (eg. Admins) and click “Choose all” below the available permissions list.
Click save

# Create user

Click “add” next to users under the COSTASIELLA section.
Add a new user and enter the user’s names and an email address in the edit screen after saving. Add the user to the group just created and click save.

# Create account for user

Click Home in the breadcrumb top left.

Click “Add” next to Email addresses under the ACCOUNTS section. 
Use the little looking glass next to “user” in the “Add email address” form to select the user just created. 
Then enter the same email address as entered when saving the user and check both the “Verified” and “Primary” boxes. 
Click Save.

Almost there, log out of the admin page by clicking LOG OUT in the top right corner. 

## 

# Login

## 

Navigate to http://localhost:8000 and log in using the user just created.

In case a “CSRF Token Failed” error message shows, click the back button in the browser and try again. It might show up in some cases during the first login in the development environment. After a refresh/retry it shouldn’t show anymore.

### 

# Social auth setup; not currently implemented. Only email authentication is supported.

# You can stop reading here.

### 

Now start your server, visit your admin pages (e.g. http://localhost:8000/d/admin/) and follow these steps:

Add a Site for your domain, matching settings.SITE_ID (django.contrib.sites app).
For each OAuth based provider, add a Social App (socialaccount app).
Fill in the site and the OAuth app credentials obtained from the provider.

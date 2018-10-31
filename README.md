# One-time Use Email Address Manager

## Features
* LDAP auth
* Optional expiration of addresses
* Multiple recipients for a single alias
* Accept/reject stats
* Dockerized!

## Requirements
* Python >= 3.5
* Some DB (SQLite is fine and is the default)

## Setup
* Copy web/config.sample.py to web/config.py and make changes as needed
* If you didn't hardcode config constants above, set envvars (`LDAP_URI`, `LDAP_BASE_DN`, `HOSTNAME` are the minimum required)
* Start the frontend (either `run_web.py` or `gunicorn`)
* Start the SMTP server (`run_smtpd.py`)

## Known issues
* Issues in validating updates silently fail and cause the create form to be filled out with the invalid data
* Missing domain management

# Wishlist Searcher

## Set up the dependencies

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the app

Create a `smtp.conf` in this same directory.  First line
should be the username for logging in to an email SMTP
server; second line should be the password.

Also, create a file called `wishlist_queries.txt` in your
home directory (on OSX, something like `~` or `/Users/me/`).
Put a different query on each line.

Then you can run the searcher with this command.

```bash
python searcher.py
```

## Packaging the app

```bash
python setup.py py2app
```

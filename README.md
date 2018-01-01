# Blockchain API
I wanted to understand the whole idea behind blockchain so built this to clear concepts


## How to run
* Create a virtual environment `mkvirtualenv [envname]` or `mkvirtualenv -p <python_version> <env_name>`

* `pip3 install -r requirements.txt`

* Set FLASK_APP by `export FLASK_APP=app.py`

* Use Postman or cURL to play with the API (http requests)
 
## Sources
* [This](hackernoon.com/learn-blockchains-by-building-one-117428612f46) is what I referred to build this out and [this](www.learningblockchains.com/lessons/Building_blockchain/) is what the author may have used and reading through it was fun.

* The following were very insightful:
    * [This](https://stackoverflow.com/questions/15479928/why-is-the-order-in-dictionaries-and-sets-arbitrary/) stackoverflow question's answer was just amazing

    * [This](https://cito.github.io/blog/f-strings/) was cool too

## Further Work?
* Dockerize this API

* Separation of concerns - move all the routes into a different file other than the main app file, basically use what Flask offers me
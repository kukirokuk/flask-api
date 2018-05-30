# Flask API

This is Flask framework based api. There must sqlite db installed in your linux system also some virtualenv activated. Clone this rep.
```sh
git clone git@github.com:kukirokuk/flask-api.git
```
Then run:
```sh
pip install -t requirements.txt
```
Next:
```
python
```
This create new sqlite database:
```
>>> from api import db
>>> db.create_all()
```
And finally start server:
```sh
python run.py
```
If you are runing this app on local host than it will be available on this url `http://127.0.0.1:8080`
You can interact with it both with frontend web page and json request.
To use its frontend web pages you need to login here `http://<your_host>:<your_port>/login`.  Afteer login you willl be able 
visit its pages, submit keys, values and get values `http://<your_host>:<your_port>/get`,  `http://<your_host>:<your_port>/set`.
To interact with this API you can also make authenticated requests. There two auth ways available. The first you need to register here `http://<your_host>:<your_port>/login` to get your credentials and then provide them in url params `http://<your_host>:<your_port>/get/<key>?username=<your_username>&api_key=<your_password>`. The second way you can use basic authentication via http headers. You should provide your username and password for every request to API. Example of get request with url params authentication `http://0.0.0.0:8080/get/some_key?username=new_user&api_key=secret_key`. In response you should receive json:
```
{
    "key": "some_key",
    "user_id": 1,
    "value": "some_value"
}
```
To make a set request you should provide a json body for request `http://127.0.0.1:8080/set/?username=new_user&api_key=secret_key`:
```
{
	"key": "new_key",
	"value": "new_value"
}
```
To run tests:
```sh
python tests.py
```
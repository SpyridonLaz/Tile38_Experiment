 
from flask import Flask, url_for, request,make_response

app = Flask(__name__)

@app.route("/endpoint",methods = ['POST'])
def webhook_listener():
	print(type(request))
	webhook_request = request.values
	print(webhook_request,request.values,request.json)
	return "200"



















app.run(host="localhost", port=8001)

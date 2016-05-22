import requests

SUCCESS = 0
FAILED = 1

def send2queue(file, queue, user=None):
	return SUCCESS
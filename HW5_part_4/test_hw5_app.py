import socket,sys
from wsgiref.simple_server import make_server

from hw5_app import SimpleApp

def test_straight_up_get():
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	s.connect((socket.getfqdn(),8888))
	s.send("GET / HTTP/1.0\r\n\r\n")

	results = ""

	while 1:
		buf = s.recv(1000)
		if not buf:
			break
		results += buf

	assert "HTTP/1.0 200 OK" in results, results
	assert "content-type: text/html" in results, results
	assert "THIS IS THE INDEX AND IT IS AWESOME" in results, results

def test_form_submission_get():
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	s.connect((socket.getfqdn(),8888))

	s.send("GET /recv?color=Maroon&cookie=Oatmeal+Chocolate+Chip HTTP/1.0\r\n\r\n")

	results= ""

	while 1:
		buf = s.recv(1000)
		if not buf:
			break
		results += buf

	assert "HTTP/1.0 200 OK" in results, results
	assert "content-type: text/html" in results, results
	assert "Favorite Color: Maroon" in results
	assert "Favorite Cookie Flavor: Oatmeal Chocolate Chip" in results

def test_image_retrieval():
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	s.connect((socket.getfqdn(),8888))

	s.send('GET /image HTTP/1.0\r\n\r\n')

	results= ""

	while 1:
		buf = s.recv(1000)
		if not buf:
			break
		results += buf

	assert "HTTP/1.0 200 OK" in results, results
	assert "content-type: image/jpg" in results, results
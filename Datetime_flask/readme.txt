docker build -t flask-clock .
docker run -d -p 8080:8080 flask-clock
docker run -d -p 8080:8080 --name flask-app flask-clock
docker stop flask-app
docker rm flask-app
# pystats

pystats: K8s "hello world" or "system metrics endpoint"

A simple web app to log requests and export system metrics. Designed for kubernetes platform development toubleshooting.

[GitHub Release](https://github.com/snowkiterdude/pystats)
[Docker Hub Release](https://hub.docker.com/r/snowkiterdude/pystats)

## Usage

View the cli arguments
```
docker run --rm snowkiterdude/pystats:latest -h
```

Run the web application in the background
```
make build-local;
make run-local;
sleep 1;
curl -v "http://localhost:8080/?fast=true";
```


## todo
  [ ] basic system stats in Prometheus formate at /metrics
  [x] multi platform image builds
    [x] build.sh to work with both mac and linux dev platforms
    [x] build one image compatible with both arm and amd

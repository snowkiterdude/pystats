# pystats

pystats: K8s "hello world" or "system metrics endpoint"

A simple web app to log requests and export system metrics. Designed for kubernetes platform development toubleshooting.

https://github.com/snowkiterdude/pystats

# Usage

View the cli arguments
```
docker run --rm snowkiterdude/pystats:latest -h
```

Run the web application in the background
```
mkdir pystats;
docker run --name pystats --rm -d -p 80:8080 -v "pystats:/var/lib/pystats" snowkiterdude/pystats:latest;
```

# todo
  * basic system stats in Prometheus formate at /metrics
  * multi platform image builds
    * build.sh to work with both mac and linux dev platforms
    * build one image compatible with both arm and amd

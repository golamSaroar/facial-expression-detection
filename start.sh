#!/bin/bash
app="facial-expression-detection"
docker build -t ${app} .
docker run --rm -p 5000:5000 \
  --name=${app} \
  -v $PWD:/var/www ${app}

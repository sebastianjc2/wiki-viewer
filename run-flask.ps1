#!/usr/bin/env pwsh

$env:FLASK_APP="flaskr"
$env:FLASK_ENV="development"
flask run -p 8080
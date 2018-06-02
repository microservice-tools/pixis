# **Pixis**  &nbsp; ![Build Status](https://travis-ci.org/microservice-tools/pixis.svg?branch=dev)

Pixis is a flexible and lightweight Python 3 module that can generate server and client files for your REST API. You provide an [OpenAPI3 Specification](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md), we generate the skeleton code to get your API up and running.

Our system allows for simple and flexible customization. The default [Jinja2](http://jinja.pocoo.org/docs/2.10/) templates can be modifed and/or replaced, so you can generate exactly the code you want. Our build file lets you specify exactly how you want your project to look like, and with a little Python, you can add custom functionality to Pixis, and even generate code in a new language!

### Currently supported server languages:
- [Python-Flask](http://flask.pocoo.org/)

### Currently supported client languages: 
- [TypeScript-Angular2](https://angular.io/)
---

# Table of Contents
* [Virtual Environment Setup](#virtual-environment-setup)
* [Installation](#installation)
* [Usage](#usage)
* [Generating a Server](#generating-a-server)
* [Generating a Client](#generating-a-client)
* [Specification File](#specification-file)
* [Configuration File](#configuration-file)

# Virtual Environment Setup
## Linux & Mac Users:
1. Install latest version of virtualenv using: `sudo pip3 install virtualenv`
2. Create virtual environment: 
`virtualenv venv`
- Activate virtual environment: 
`source venv/bin/activate`
- Deactivate virtual environment:
`deactivate`
# Installation
1. Clone this project
2. Activate virtualenv
3. Two options to install: 
    - Using pip3:
        - `pip3 install pixis/`
    - Using setup.py:
        - `cd pixis`
        - `python3 setup.py develop`
- Uninstall:
    - `pip3 uninstall pixis`

**Note: If you are having issues installing on Mac OSX try**
    - pip3 install pbr certifi

# Usage
**Pixis default behavior**: Implementation is *Flask*, Output is *build/*, Templates is *templates/*, Specification file is *swagger.yaml*

`$ pixis`: Looks for **build.py** in the current directory.

| COMMAND | LONG        | ARGUMENTS     | DESCRIPTION                                                      |
|---------|-------------|---------------|------------------------------------------------------------------|
| -h      | --help      | N/A           | Displays Pixis information and commands                          |
| -b      | --build     | build_file    | Set build file location, default: `build.py`                     |
| -o      | --output    | output_dir    | Set output directory location, default: build/                   |
| -t      | --templates | templates_dir | Set local template directory, default: templates/                |
| -v      | --verbose   | N/A           | Displays information about what files were or were not generated |


Refer to `BUILD.md` for more information on the build file

---

## **Quick Start**

We recommend using a virtual environment when generating and testing generated code.

## Generating a server

This example will use our **samples/python-flask-server/** directory, containing **build.py** and **swagger.yaml**

```bash
$ cd samples/python-flask-server/
$ pixis [-b build.py]
$ cd build
$ pip3 install -r requirements.txt
$ pip3 install .
$ my_flask_server
```

- A server should be opened on your localhost
- To test a route, append to the basepath: `/pet/0`
- You should see the route printed onto the screen
- Future versions will have more exciting examples!
    
To run in a docker container:
-   `$ docker build -t your_tag .`
-   `$ docker run -p 8080:8080 your_tag .`

## Generating a client
To use the Angular2/TypeScript client, some prerequisites need to be installed. Earlier versions are untested.
- [**node.js**](https://nodejs.org/en/) >= 8.6.0 
- **npm** >= 5.6.0 
    - installed with node.js
    - get latest version with: `[sudo] npm install npm -g`
- **angular/cli** >= 1.4.6 
    - `[sudo] npm install -g @angular/cli@latest`

---

This example will use our ready to go Angular2 project **sample-project** in **samples/typescript-angular-client**. Our project contains edits (imports and API usage) that a newly generated Angular2 project will not have. Instruction for generating a new Angular2 project can be found [here](https://cli.angular.io/).

**samples/typescript-angular-client** includes **build.py** and **swagger.yaml**

```bash
$ cd sample/typescript-angular-client
$ pixis build.py
$ mv services/ sample-project/src/
$ cd sample-project
$ npm install
```
To run the client: `npm start` or `ng serve`
- Go to the url that the client is being served to (ex. http://localhost:4200)
- If you are also running a server on localhost, you will run into a CORS issue which can be resolved using a google chrome extension (https://chrome.google.com/webstore/detail/allow-control-allow-origi/nlfbmbojpeacfghkpbjhddihlkkiljbi?utm_source=chrome-app-launcher-info-dialog)
- If using our modified angular2 component files, open console (f12) and you should see **getPetById(0)**, meaning that the client is using the generated files. The server will also receive the requests.

To run in a docker container:
- `$ docker build -t your_tag .`
- `$ docker run -p 4200:4200 your_tag .`


# Specification File
Specification file according to OpenAPI 3.0 Specification guidelines
https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md

# Build File (`build.py`)
Refer to `BUILD.md`

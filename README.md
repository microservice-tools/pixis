# **Pixis**    [![Build Status](https://travis-ci.org/jchen463/Rest-Codegen.svg?branch=dev)](https://travis-ci.org/jchen463/Rest-Codegen)

# What is Pixis?
description

# Table of Contents
* [Virtual Environment Setup](#virtual-environment-setup)
* [Installation](#installation)
* [Usage](#usage)
* [Generating a Server](#generating-a-server)
* [Generating a Client](#generating-a-client)
* [Specification File](#specification-file)
* [Configuration File](#configuration-file)

# Virtual Environment Setup
## Linux Users:
1. Install latest version of virtualenv using: `sudo pip3 install virtualenv`
2. Create virtual environment: 
`virtualenv venv`
- Activate virtual environment: 
`source venv/bin/activate`
- Deactivate virtual environment:
`deactivate`
# Installation
1. Clone this project (Rest-Codegen)
2. Activate virtualenv
3. Two options to install: 
    - Using setup.py:
        - `cd Rest-Codegen`
        - `python3 setup.py develop`
    - Using pip3:
        - `pip3 install Rest-Codegen/`
- Uninstall:
    - `pip3 uninstall rest-codegen`

# Usage

Command line options will be included soon!

**Default settings for Codegen:**
- Looks for a user-defined build file named **build.py** in the current working directory. If it exists, run it
- If specification file is not specified in the build file, looks for a specification file named **swagger.yaml** in the current working directory
- If a folder named **templates/** exists in current working directory, then Codegen will use templates inside that folder instead of default templates, as long as those templates are the same name as the defaults
- Codegen will generate a Flask server directory named **flask-server-generated** in the current working directory

**Run Codegen using default settings with:** `$ codegen`

**Run Codegen using a build file:** `$ codegen build.py`

Sample build file with available options can be found in our repository's **SAMPLE/** directory (documentation soon!)

---

## **Quick Start**

We recommend using a virtual environment when generating and testing generated code.

## Generating a server

Server generation steps can be done in either our project's **SAMPLE/** directory, or in a new directory containing a specification file named **swagger.yaml**. A python build file is optional. Sample build file and specification file can be found in the **SAMPLE/** directory.

1. `$ codegen [build.py]`
    - A directory named **flask-server-generated/** should have been generated
1. `$ cd flask-server-generated`
1. `$ pip3 install -r requirements.txt`
    - The Flask server dependencies will be installed
1. `$ python3 -m flask_server`
    - A server should be opened on your localhost
    - To test a route, append to the basepath: `/pet/0`
    - You should see the route printed onto the screen
    - Future versions will have more exciting examples!

---

## Generating a client
To use the Angular2/TypeScript client, some prerequisites need to be installed. Earlier versions are untested.
- **node.js** >= 8.6.0 
    - https://nodejs.org/en/
- **npm** >= 5.6.0 
    - installed with node.js
    - get latest version with: `[sudo] npm install npm -g`
- **angular/cli** >= 1.4.6 
    - `[sudo] npm install -g @angular/cli@latest`

---

For a quick proof-of-concept, a ready to go Angular2 project **myproject** can be found in **SAMPLE/**. Without generating the Angular2 project, follow the steps in the section below, but skip step 3.

- `$ ng new myproject`
    - Creates a new Angular2 project named **myproject/** in the current working directory

Client generation steps can be done in either the Angular2 **myproject/src/** directory, or in a new directory. A specification file (default **swagger.yaml**) and a python build file (default **build.py**) must be in the directory. 

This guide will generate inside the Angular2 project, and assume that the specification file and build file are present.

If you are not executing Codegen in **myproject/src/**, you must move the generated directory into **myproject/src/**.

A build file is necessary to tell Codegen to generate TypeScript client code instead of Flask server code. This process will be changed in the future.
- In **build.py** (sample can be found in **SAMPLE/**), change:
    - `LANGUAGE='flask'` to 
    - `LANGUAGE='typescript'`

---

1. `$ cd myproject/src`
1. `$ codegen build.py`
    - A directory named **services** should have been generated
1. Modify **app.component.ts** and **app.module.ts** inside **myproject/src/app** url as the server you are trying to connect to
1. `$ cd ..`
1. `$ npm install`
1. `$ ng serve`
    -  Go to the url that the client is being served to (ex. http://localhost:4200)
    - If you are also running a server on localhost, you will run into a CORS issue which can be resolved using a google chrome extension (https://chrome.google.com/webstore/detail/allow-control-allow-origi/nlfbmbojpeacfghkpbjhddihlkkiljbi?utm_source=chrome-app-launcher-info-dialog)
    - If using our modified angular2 component files, open console (f12) and you should see **getPetById(0)**, meaning that the client is using the generated files. The server will also receive the requests.   

---

# Specification File
Specification file according to OpenAPI 3.0 Specification guidelines
https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md

# Configuration File
The configuration file can be used in order to specify the language that the user wants to generate, the specification file to be used, and the output directory name for the generated code. 

Please refer to **SAMPLE/build.py** for details.

1. `SPEC`: refers to the name of the specification file
2. `LANGUAGE`: refers to the language the user wants to generate
    - only python generation is available for server as of now
    - only typescript generation is available for client as of now
3. `PROJECT_NAME`: refers to the name of output directory where the code generation will live

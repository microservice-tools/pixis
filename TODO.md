# **TODO**

## **5/21 - 5/28**

### DOCUMENTATION
- docstrings on functions/classes
- type hints on functions/parameters
- finish markdown docs
- check how pycharm parses comments

### TESTING
- pytest
- Command line tests:
    - pixis
    - pixis -b buildfiles/build1.py
    - pixis --build buildfiles/build1.py
    - pixis -o OUT
    - pixis --output OUT
    - pixis -t mytemplates
    - pixis --templates mytemplates


### VERBOSE
- possibly using the python logger module
- print which files we're generating, which templates we're using, where we're generating them to, etc.
- once hash checking and file ignore is in then also print out what files we're not generating

### FINISH SCHEMAS
- finish property class
- make sure everything from the spec is represented
- check in with James about what we were talking about (getType being the schema handler)

### ITERATIVE DEVELOPMENT
- hashes for generated files
- hidden pixis file to record the hashes of files we generate
- when we see that we're about to generate a file that already exists, check the hash, and if the hashes are different, either don't generate or generate under a different name

---
## Templates
- sorting functions/classes alphabetically
- double check module imports!!!
- angular2
    - encodeURIcomponent part needs to be fixed
    - POST methods aren't being generated correctly
---
## Security
- https
- authentification schemes (OAUTH2)
- fix security vulnerability of one of the js packages included in the angular2 client
---
## Alternate servers
- i.e. one path specifies a specific server
---

## Additional languages
---

## Docker & Kubernetes support
---

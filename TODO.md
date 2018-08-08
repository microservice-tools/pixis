# **TODO**

### DOCUMENTATION
- google style

### TESTING
- pytest
- Command line tests:
    - `pixis`
        - Expected: generate all python files in build folder, etc
    - `pixis -b buildfiles/build1.py` and `pixis --build buildfiles/build1.py`
    - `pixis -b doesntexist.py`
        - Expected: program exits and says specified build file doesn't exist
    - `pixis -o out` and `pixis --output out`
    - `pixis -t mytemplates` and `pixis --templates mytemplates`
 
- Template Context tests
- openapi.py functions unit test
- config.py unit test
- emit_template unit test




### VERBOSE
- possibly using the python logger module
- print which files we're generating, which templates we're using, where we're generating them to, etc.
- once hash checking and file ignore is in then also print out what files we're not generating

### FINISH SCHEMAS!!!!!!!!
- finish property class
- make sure everything from the spec is represented
- check in with James about what we were talking about (getType being the schema handler)

---
## Templates
- sorting functions/classes alphabetically
- double check module imports!!!
- angular2
    - encodeURIcomponent part needs to be fixed
    - POST methods aren't being generated correctly
---
## Alternate servers
- i.e. one path specifies a specific server
---

## Additional languages
---

## Docker & Kubernetes support
---

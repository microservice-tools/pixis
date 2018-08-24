# **TODO**

## Schemas
- Fix schema representation in openapi.py (progress in schemas branch)
- Fix how we pull schemas from spec into template context in template_handler.py (also probably rename to template_context.py)
- Need to figure out how to decide which schemas to generate (things like properties are schemas as well, but simple schemas shouldn't be generated. Need to look more into this)
- Sort resulting schemas alphabetically
---
## Testing (pytest)
- Command line tests:
    - `pixis`
        - Expected: generate all python files in build folder, etc
    - `pixis -b buildfiles/build1.py` and `pixis --build buildfiles/build1.py`
    - `pixis -b doesntexist.py`
        - Expected: program exits and says specified build file doesn't exist
    - `pixis -b asdf`
        - Expected: program exits and says specified build file is not a Python file
    - `pixis -o out` and `pixis --output out`
    - `pixis -t mytemplates` and `pixis --templates mytemplates`
- Template Context tests
- openapi.py functions unit test
- config.py unit test
- emit_template unit test
---
## Logging & Verbose
- logger module
---
## Templates
- angular2
    - encodeURIcomponent part needs to be fixed
    - POST methods aren't being generated correctly
---
## Accommodating template repositories
---
## Alternate servers
- i.e. one path specifies a specific server
---

## Additional languages
---

## Docker & Kubernetes support
---

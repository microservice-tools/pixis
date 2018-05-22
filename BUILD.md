# **Build file**

Users can define a Python3 build file to set code generation options and implement custom behavior

---

## Build file variables

| VARIABLE       | TYPE            | DESCRIPTION                                           |
|----------------|-----------------|-------------------------------------------------------|
| SPEC           | string          | Relative filepath to specification file (json/yaml)   |
| TEMPLATES      | string          | Relative filepath to local custom templates directory |
| IMPLEMENTATION | string OR class | One of {'flask', 'angular2} OR a user-defined class   |
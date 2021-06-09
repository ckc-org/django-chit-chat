django-chit-chat [<img src="https://ckcollab.com/assets/images/badges/badge.svg" alt="CKC" height="20">](https://ckcollab.com)
==========
chat for projects we help maintain @ [ckc](https://ckcollab.com)


## installing

```bash
pip install django-chit-chat
```

```python
# settings.py
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",

    # ... add chit_chat
    "chit_chat",
)
```

## distributing

```bash
# change version in setup.cfg
$ ./setup.py sdist
$ twine upload dist/*
```

## tests

```bash
$ docker build -t django-chit-chat . && docker run django-chit-chat pytest
```

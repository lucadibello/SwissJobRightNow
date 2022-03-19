# SwissJobRightNow - Find a your dream job in very little time

## Introduction

Find your dream job with SwissJobFinder. This suite allows you to send applications to a large number of Swiss companies operating in a certain (user-defined) field in an area predefined by the user at startup.

Each person has different potentialities and requirements, that's why SwissJobFinder is extremely flexible in order to satisfy (almost) every kind of user: you can modify every single detail related to the search, the generation and the sending of applications.

## Showcase


## Setup

### Config file

In the config folder you can find an example config file called "config.example.json". To create your own config file you simply need to:

1. Copy the example config file
2. Rename it to "config.json".
3. Modify the settings of your choice, see chapter **config file** for more information related to the possibile settings.

### Yarn + NodeJS

You need to have Yarn package manager and NodeJS correctly installed and set up on your system (*yarn* and *node* commands are available into the sheel)

### Python package requirments

You can install all the required package using pip3 (Python package manager) by executing this command:

```bash
pip install -r requirements.txt
```

## Usage examples

### Looking for an IT position in companies in canton Zurich

```bash
python3 src/swissjobfinder.py -C Zurich Informatik
```

### Search for work by contacting both individuals and companies in Lugano region

```bash
python3 src/swissjobfinder.py -A -R Lugano Parrucchiere
```

**Important note:** It is best to write the kind of job you want using the native language of the place where you are actually looking for work. The program will find more results this way

## Conclusion

This software was initially developed for a personal need of mine: I needed to find an internship position but I only had 3 weeks to do it, this tool was born from my need to contact a multitude of companies in a short time. Only now, after a year since its development, I decided to make it more presentable (before it was spaghetti-code) and make it public.

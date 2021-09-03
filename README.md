# archive

An archive of projects, experiments, and creative dead-ends.

This is also a lazy static site generator designed around how I manage my
project documentation. The **main** branch has the site generator and the
**archive** branch has the site content.

## Motivation

I want to share all of my projects but it takes a lot of time to write articles
about them. On GitHub every project can have a README to provide at least some
minimal context about what's going on. What if I could just do that for every
project, regardless of whether it makes sense to make a GitHub repository for
each one?

This simple static site generator will find project directories which contain
README files and create pages for them. Media files that are linked relative to
the README will be included in the output. The resulting website can be
uploaded to GitHub Pages or any other static site host.

## Usage

Create a **config.yml** file like so:

```yaml
output_directory: docs
project_directories:
  - "/your/cool/stuff"
```

Then run `python update.py`. The static site will appear under the path
specified for the `output_directory` key.

### Rebuilding on Changes

While adding new READMEs it is convenient to have the output update
automatically.

Install [yq](https://github.com/mikefarah/yq) and [nodemon](https://nodemon.io/).

Then run:

```
nodemon --ext md --watch "$(yq e '.project_directories[0]' config.yml)" --exec "rm -rf docs && python3 update.py"
```


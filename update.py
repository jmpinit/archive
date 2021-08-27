from pathlib import Path
import yaml
from markdown2 import Markdown
from bs4 import BeautifulSoup
import chevron
from slugify import slugify
import shutil


def has_readme(path):
    return (path / 'README.md').is_file()


def index_project_dir(project_dir, output_path):
    project_dir = Path(project_dir)

    documented_projects = list(filter(has_readme, project_dir.rglob('**/')))

    with open('templates/project.html', 'r') as project_template_file:
        project_template = project_template_file.read()

    pages_created = []

    for project_path in documented_projects:
        readme_path = project_path / 'README.md'

        # Read the README
        with open(readme_path, 'r') as readme_file:
            readme = readme_file.read()

        # Convert to HTML
        mkdn = Markdown()
        readme_html = mkdn.convert(readme)
        readme_soup = BeautifulSoup(readme_html, 'html.parser')

        # Fill in the template by pulling things from the markdown via the HTML

        proj_name = readme_soup.h1.get_text()
        readme_soup.h1['class'] = 'title'

        proj_slug = slugify(proj_name)

        if proj_name is None:
            raise Exception('Failed to find a project name')

        proj_info = {
            'slug': proj_slug,
            'title': proj_name,
            'body': readme_soup.prettify(),
        }

        proj_page = chevron.render(project_template, proj_info)

        proj_soup = BeautifulSoup(proj_page, 'html.parser')

        if output_path.is_file():
            raise Exception('Output path is a file')

        if not output_path.exists():
            output_path.mkdir()

        project_out_path = output_path / proj_slug
        project_out_path.mkdir()

        # Extract and copy over any images that were used

        media_path = project_out_path / 'media'
        if not media_path.exists():
            media_path.mkdir()

        for tag in proj_soup.find_all('img'):
            image_src_path = project_path / tag['src']

            if not image_src_path.exists():
                raise Exception(f'Image {image_src_path} does not exist')

            image_dest_path = media_path / tag['src']

            shutil.copy(image_src_path, image_dest_path)

            # Rewrite the page to reference the image in the output location
            tag['src'] = f'media/{tag["src"]}'

        project_page = project_out_path / f'index.html'
        with open(project_page, 'w') as project_page_file:
            project_page_file.write(proj_soup.prettify())

        pages_created += [{**proj_info, 'path': str(project_page)}]

    return pages_created


def main():
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    output_path = Path() / config['output_dir']

    # Create the pages

    pages = []
    for project_dir in config['project_directories']:
        pages += index_project_dir(project_dir, output_path)

    # Create the index
    with open('templates/index.html', 'r') as index_template_file:
        index_html = chevron.render(index_template_file.read(), {'pages': pages})

    with open(output_path / 'index.html', 'w') as index_file:
        index_file.write(index_html)


if __name__ == '__main__':
    main()

import datetime
import os
import pybtex
import setuptools
import yaml
import shutil
import importlib.resources as pkg_resources
import subprocess
from livereload import Server, shell
from pybtex.database import parse_file
from pybtex.plugin import find_plugin
from livereload import Server

YEAR = datetime.datetime.now().year
DATA = yaml.safe_load(open(
    pkg_resources.files(__package__).joinpath('data/data.yaml'),
    'r',
    encoding='utf-8'))
TITLE = DATA.get('title', '')
EMAIL = DATA.get('email', '')
DOMAIN = DATA.get('domain', '')
LINKS = DATA.get('links', [])
TEMPLATE = open(pkg_resources.files(__package__).joinpath('data/template.html'),'r', encoding='utf-8').read()

PREPRINT_BIB = pkg_resources.files(__package__).joinpath('bib/prep.bib')
JOURNAL_BIB = pkg_resources.files(__package__).joinpath('bib/jrnl.bib')
CONFERENCE_BIB = pkg_resources.files(__package__).joinpath('bib/conf.bib')
SELECTED_BIB = pkg_resources.files(__package__).joinpath('bib/selected.bib')
TEX_DIR = pkg_resources.files(__package__).joinpath('tex')
ASSET_DIR = pkg_resources.files(__package__).joinpath('assets')

def nav_html(nav_items):
    nav_html = ""
    for name, url in nav_items.items():
        nav_html += f'<li class="nav-item"><a class="nav-link" href="{url}">{name}</a></li>'
    return nav_html

nav_items = {
    "Home": "",
    "Values": "values",
    "People": "people",
    "Research": "research",
    "Publications": "publications",
    "Software": "software",
    "Facilities": "facilities",
    "News": "news",
}

NAV = nav_html(nav_items)

# Constants
BUILD_DIR = '_build'

def generate_html(output, content):
    output = os.path.join(output, "index.html")
    """Generates an HTML file by replacing placeholders in the TEMPLATE."""
    html_content = TEMPLATE.format(content=content, title=TITLE, year=YEAR, nav=NAV, email=EMAIL)
    for link in LINKS:
        html_content = html_content.replace(
            f"{{{link['name']}}}",
            f"""<a href="{link['url']}">{link['name']}</a>"""
        )

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"Generated {output} successfully.")

def generate_publications_html(output):
    content = f"""
    <h1>Publications</h1>
    <h2>Preprints</h2>
    <table>
    {formatted_bib(PREPRINT_BIB, 'P')}
    </table>
    <hr>
    <h2>Journal Publications</h2>
    <table>
    {formatted_bib(JOURNAL_BIB, 'J')}
    </table>
    <hr>
    <h2>Conference Publications</h2>
    <table>
    {formatted_bib(CONFERENCE_BIB, 'C')}
    </table>
    """    
    generate_html(output, content)

def generate_index_html(output):
    news_html = formatted_news(DATA.get('news', '')[:5])  # Limit to the first 5 news items
    packages_html = "\n".join([
        f"""
        <li>
            <strong><a href="{pkg['url']}">{pkg['name']}</a></strong>: {pkg['description']}
        </li>
        """ for pkg in DATA.get('packages', '')
    ])

    # Generate HTML list for publications
    publications_html = formatted_bib(SELECTED_BIB, 'S')
    index = DATA.get('index', [])
    middle = "<hr>\n".join([
        f"""
        <h2>{entry['name']}</h2>
        <p>{entry['description']}</p>
        <p><a href="{entry['link']['url']}">{entry['link']['description']} >></a></p>
        """
        for entry in index['entries']])

    content = f"""
    <h1>Home</h1>
    <img class="home" src=/assets/img/index.jpg alt="photo" class="img-fluid">
    <p>
        {index['description']}
    </p>
    <hr>
        {middle}
    <hr>
    </p>
    <h2>News</h2>
    <table>
        {news_html}
    </table>
    <p>
    <a href="news">See more news >></a>
    </p>
    <hr>
    <h2>Selected Publications</h2>
    <table>
        {publications_html}
    </table>
    <p>
    <a href="publications">See more publications >></a>
    </p>
    """
    generate_html(output, content)

def generate_values_html(output):
    values = DATA.get('values', [])
    """Generates the values page."""
    values_html= "\n".join([
        f"""
        <li>
        <strong>{value['name']}</strong>: {value['description']}
        </li>
        """ for value in values['entries']
    ])
    content = f"""
    <h1>Values</h1>
    <p>
        {values['description']}
    </p>
    <ul>
    {values_html}
    </ul>
    """
    generate_html(output, content)

def generate_research_html(output):
    research = DATA.get('research', [])
    content =  f"""
    <h1>Research</h1>
    { research.get('description', '') }
    <hr>
    {
        "<hr>\n".join([f"""
    <div class="row">
    <div class="col-md-6">
    <h2>{res['name']}</h2>
    {res['description']}
    </div>
    <div class="col-md-6 d-flex justify-content-center">
    <img src={res['img']} class="research">
    </div>
    </div>
    """ for res in research['entries']])
    }
    """
    generate_html(output, content)
    
def generate_news_html(output):
    """Generates the news page."""
    news_html = formatted_news(DATA.get('news', []))
    content = f"""
    <h1>News</h1>
    <table>
    {news_html}
    </table>
    """
    generate_html(output, content)

def generate_software_html(output):
    software = DATA.get('software', [])
    """Generates the software page."""
    software_html= "\n".join([
        f"""
        <li>
        <strong><a href={value['url']}>{value['name']}</a></strong>: {value['description']}
        </li>
        """ for value in software['entries']
    ])
    content = f"""
    <h1>Software</h1>
    <p>
        {software['description']}
    </p>
    <ul>
    {software_html}
    </ul>
    """
    generate_html(output, content)

def generate_facilities_html(output):
    facilities = DATA.get('facilities', [])
    """Generates the facilities page."""
    facilities_html= "\n".join([
        f"""
        <li>
        <strong>{value['name']}</strong>: {value['description']}
        </li>
        """ for value in facilities['entries']
    ])
    content = f"""
    <h1>Facilities</h1>
    <p>
        {facilities['description']}
    </p>
    <ul>
    {facilities_html}
    </ul>
    """
    generate_html(output, content)

def formatted_news(news):
    return "\n".join([
        f"""
        <tr valign="top"><td width="120px"><i>{news['date']}</i></td> <td>{news['description']} [ <a href="{news['link']}"> Link </a> ]<td></tr>
        """ for news in news])
        
def formatted_social(social):
    """Formats the social media links into HTML."""
    if not social:
        return ""
    else:
        return f"""
        [ {" | ".join([f'<a href="{link["url"]}">{link["name"]}</a>' for link in social])} ]
        """
def formatted_bib(bib_file, letter):
    bib_data = parse_file(bib_file)
    style = find_plugin('pybtex.style.formatting', 'unsrt')()
    
    def bold_names(entry_text):
        return entry_text.replace("Sungho Shin", "<strong>Sungho Shin</strong>")
    
    return "\n".join(reversed([
        """<tr valign="top"><td>[{letter}{index}]</td><td>{entry}</td></tr>""".format(
            letter=letter, index=i, entry=bold_names(entry.text.render_as('html'))
        )
        for i, entry in enumerate(style.format_bibliography(bib_data), start=1)
    ]))

def generate_people_html(output):
    people = DATA.get('people', [])
    content = f"""
    <h1>People</h1>
    <h2>Principal Investigator</h2>
    <div class="full">
    <div class="left">
    <img class="profile-picture" src={people['pi']['img']} alt="photo" class="img-fluid">
    </div>
    <div class="right">
    <h3>{people['pi']['name']}</h3>
    {people['pi']['title']}
    <br>
    {people['pi']['address']}
    <br>
    [ <a href="mailto:{people['pi']['email']}">{people['pi']['email']}</a> | <a href="tel:{people['pi']['phone']}">{people['pi']['phone']}</a> ]
    <br>
    { formatted_social(people['pi']['social']) }
    </div>
    </div>
    <h4>Affiliations </h4>
    <ul>
    {
    "\n".join([
        f"<li>{affiliation}</li>" for affiliation in people['pi']['affiliations']
    ])
    }
    </ul>
    <h4>Education and Training</h4>
        <ul>
        {
        "\n".join([
                f"<li>{education}</li>" for education in people['pi']['education']
                ])
                }
        </ul>
    <h4>Bio</h4>
    {people['pi']['bio']}
    <hr>
    {
    "<hr>\n".join([
    f"""
    <h2>{rolename}</h2>
    {
        "\n".join([
            f"""
                <div class="full">
                <div class="left">
                <img class="profile-picture" src={person['img']} alt="photo" class="img-fluid">
                </div>
                <div class="right">
                <h3>{person['name']}</h3>
                <p>
                [ <a href="mailto:{person['email']}">{person['email']}</a> ]
                <br>
                { formatted_social(person['social']) }
                </p>
                <p>{person['bio']}</p>
                </div>
                </div>
                """ for person in people.get(role, [])
        ])
    }
    """
     for (rolename, role) in [('Postdoctoral Associates', 'postdocs'), ('Graduate Students', 'graduates'), #('Undergraduate Students', 'undergraduates'), 
                              ('Visitors', 'visitors')]])
    }
    <hr>
    <h2>Alumni</h2>
    {
    " | ".join([
    f"{alumni['name']} ({alumni['role']})" for alumni in people.get('alumni', [])
    ])
    }
    """
    generate_html(output, content)
    
def build():
    """Main function to generate the HTML content and create the index.html file."""
    # Generate the HTML file
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)
    
    # Combine all content
    generate_index_html(BUILD_DIR)
    generate_values_html(os.path.join(BUILD_DIR, "values"))
    generate_people_html(os.path.join(BUILD_DIR, "people"))
    generate_facilities_html(os.path.join(BUILD_DIR, "facilities"))
    generate_software_html(os.path.join(BUILD_DIR, "software"))
    generate_news_html(os.path.join(BUILD_DIR, "news"))
    generate_publications_html(os.path.join(BUILD_DIR, "publications"))
    generate_research_html(os.path.join(BUILD_DIR, "research"))
    
    # Create a CNAME file
    cname_path = os.path.join(BUILD_DIR, "CNAME")
    with open(cname_path, "w") as f:
        f.write(DOMAIN)

    # Move assets to the build directory
    assets_src = pkg_resources.files(__package__).joinpath('assets')
    assets_dest = os.path.join(BUILD_DIR, 'assets')
    shutil.copytree(assets_src, assets_dest)

def serve():
    # Do initial build before starting
    print("Running initial build...")
    build()

    server = Server()
    server.watch(
        pkg_resources.files(__package__),
        build,
    )
    server.serve(root=BUILD_DIR, port=8000) 

def cv():
    print("Generating CV...")
    subprocess.run(['latexmk', 'shin'], cwd=TEX_DIR, check=True)
    # Move assets to the build directory
    shutil.copy(TEX_DIR.joinpath('shin.pdf'), ASSET_DIR)
    
def deploy():
    print("Running initial build...")
    cv()
    build()
    
    """Deploy the contents of _build to the gh-pages branch."""
    # Define the branch name
    branch_name = "gh-pages"

    # Ensure the _build directory exists
    if not os.path.exists(BUILD_DIR):
        raise Exception(f"The build directory {BUILD_DIR} does not exist. Run the build process first.")

    # Initialize a new Git repo inside the _build directory
    subprocess.run(['git', 'init'], cwd=BUILD_DIR, check=True)

    # Set up the remote repository (assumes origin is set up)
    subprocess.run(['git', 'remote', 'add', 'origin', 'git@github.com:mit-shin-group/mit-shin-group.github.io.git'], cwd=BUILD_DIR, check=True)

    # Checkout a new branch (or switch to it if it exists)
    subprocess.run(['git', 'checkout', '-B', branch_name], cwd=BUILD_DIR, check=True)

    # Add all the files to staging area
    subprocess.run(['git', 'add', '.'], cwd=BUILD_DIR, check=True)

    # Commit the changes
    subprocess.run(['git', 'commit', '-m', 'Deploy to GitHub Pages'], cwd=BUILD_DIR, check=True)
    # Force push to the gh-pages branch
    subprocess.run(['git', 'push', '--force', '--set-upstream', 'origin', branch_name], cwd=BUILD_DIR, check=True)

    print("Successfully deployed to GitHub Pages.")


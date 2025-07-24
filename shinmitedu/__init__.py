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

PREPRINT_BIB = pkg_resources.files(__package__).joinpath('data/prep.bib')
JOURNAL_BIB = pkg_resources.files(__package__).joinpath('data/jrnl.bib')
CONFERENCE_BIB = pkg_resources.files(__package__).joinpath('data/conf.bib')
SELECTED_BIB = pkg_resources.files(__package__).joinpath('data/selected.bib')

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
    news_html = "\n".join([
        f"""
        <li>
        {news['description']} <i>{news['date']}</i> [ <a href="{news['link']}"> Link </a> ]
        </li>
        """ for news in DATA.get('news', '')
    ])

    packages_html = "\n".join([
        f"""
        <li>
            <strong><a href="{pkg['url']}">{pkg['name']}</a></strong>: {pkg['description']}
        </li>
        """ for pkg in DATA.get('packages', '')
    ])

    # Generate HTML list for publications
    publications_html = formatted_bib(SELECTED_BIB, 'S')

    content = f"""
    <h1>Home</h1>
    <img class="home" src=/assets/img/index.jpg alt="photo" class="img-fluid">
    <p>
        {DATA.get('intro', '')}
    </p>
    <hr>
    <h2>Group Overview</h2>
    <p>
        {DATA.get('overview', '')}
    </p>
    <p>
    <a href="research">Read more about our research >></a>
    <hr>
    </p>
    <h2>News</h2>
    <ul>
        {news_html}
    </ul>
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

def generate_news_html(output):
    news = DATA.get('news', [])
    """Generates the news page."""
    news_html = "\n".join([
        f"""
        <li>
        {news['description']}  <i>{news['date']}</i> [ <a href="{news['link']}"> Link </a> ]
        </li>
        """ for news in DATA.get('news', '')
    ])
    content = f"""
    <h1>News</h1>
    <ul>
    {news_html}
    </ul>
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
    return "\n".join(reversed([
        """<tr valign="top"><td>[{letter}{index}]</td><td>{entry}</td></tr>""".format(letter=letter, index=i, entry=entry.text.render_as('html'))
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
     for (rolename, role) in [('Postdoctoral Associates', 'postdocs'), ('Graduate Students', 'graduates'), ('Undergraduate Students', 'undergraduates'), ('Visitors', 'visitors')]])
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

def deploy():
    print("Running initial build...")
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
    subprocess.run(['git', 'remote', 'add', 'origin', 'git@github.com:MadNLP/madsuite.github.io.git'], cwd=BUILD_DIR, check=True)

    # Checkout a new branch (or switch to it if it exists)
    subprocess.run(['git', 'checkout', '-B', branch_name], cwd=BUILD_DIR, check=True)

    # Add all the files to staging area
    subprocess.run(['git', 'add', '.'], cwd=BUILD_DIR, check=True)

    # Commit the changes
    subprocess.run(['git', 'commit', '-m', 'Deploy to GitHub Pages'], cwd=BUILD_DIR, check=True)
    # Force push to the gh-pages branch
    subprocess.run(['git', 'push', '--force', '--set-upstream', 'origin', branch_name], cwd=BUILD_DIR, check=True)

    print("Successfully deployed to GitHub Pages.")
# import os
# import subprocess
# from pathlib import Path
# import markdown
# import shutil

# root_dir = Path(__file__).parent.parent
# content_dir = root_dir / "content"
# template_dir = root_dir / "template"
# people_dir = root_dir / "people"
# img_dir = root_dir / "img"
# css_dir = root_dir / "css"
# bib_dir = root_dir / "bib"
# ads_dir = root_dir / "ads"
# tex_dir = root_dir / "tex"
# output_dir = root_dir / "build"
# extra_dir = root_dir / "extra"

# ADS = ["ad1.html"]
# KEYWORDS = {
#     "{ year }": "2025",
#     "{ email }": "sushin@mit.edu",
# }
# HYPERLINKS = {
#     "MIT": "https://web.mit.edu",
#     "Sungho Shin": "people",
#     "Massachusetts Institute of Technology": "https://web.mit.edu",
#     # ... (other hyperlinks)
#     "email Sungho": "mailto:sushin@mit.edu",
# }

# WATCHDIR = ["build", "content", "template", "img", "css"]

# abbrvnames = ["S. Shin"]
# dependencies = ["bibtex2html", "pdflatex", "pdf2svg"]
# cvversions = ["shin", "shin-short"]
# bibfiles = ["prep", "thes", "jrnl", "conf", "tech", "invt", "pres", "selected"]
# figfiles = ["fig-1", "fig-2", "fig-3", "fig-4"]

# PDFLATEX = 'pdflatex -halt-on-error'
# BIBTEX = 'bibtex -terse'
# BIBTEX2HTML = 'bibtex2html'
# PDF2SVG = 'pdf2svg'

# def run(command):
#     subprocess.run(command, shell=True, check=True)

# def check_dependencies():
#     for dep in dependencies:
#         try:
#             run(f"which {dep}")
#         except subprocess.CalledProcessError:
#             print(f"Error: Dependency {dep} is not installed. Please install it to build the website.")
#             return False
#     return True

# def build_cv():
#     print("Building CV")
#     os.chdir(tex_dir)

#     for cvname in cvversions:
#         run(f"{PDFLATEX} {cvname}")
#         for f in bibfiles:
#             try:
#                 run(f"{BIBTEX} {f}")
#             except subprocess.CalledProcessError:
#                 pass
            
#             with open(f"{tex_dir}/{f}.bbl") as file:
#                 content = file.read().replace("S. Shin", "{\\bf S. Shin}")
#             with open(f"{tex_dir}/{f}.bbl", "w") as file:
#                 file.write(content)
#         run(f"{PDFLATEX} {cvname}")
#         run(f"{PDFLATEX} {cvname}")

# def build_extra():
#     print("Building Extra")
#     os.chdir(extra_dir)
#     for f in figfiles:
#         run(f"{PDFLATEX} {f}")
#         run(f"{PDF2SVG} {f}.pdf {f}.svg")
#         os.replace(f"{extra_dir}/{f}.svg", f"{img_dir}/{f}.svg")

# def build(dev=False, cv=True, extra=True, clean=True):
#     if not check_dependencies():
#         return
    
#     if cv:
#         build_cv()
#     if extra:
#         build_extra()
    
#     print("Building website")
    
#     if clean:
#         if output_dir.exists():
#             for item in output_dir.glob("*"):
#                 if item.is_dir():
#                     shutil.rmtree(item)
#                 else:
#                     item.unlink()
#     output_dir.mkdir(exist_ok=True)
#     (output_dir / "img").mkdir(exist_ok=True)
#     (output_dir / "css").mkdir(exist_ok=True)
    
#     for folder in ["img", "css"]:
#         os.replace(root_dir / folder, output_dir / folder)
    
#     os.replace(tex_dir / "shin.pdf", output_dir / "shin.pdf")

#     nav = nav_html(nav_items)

#     html_names = [name.replace(" ", "&nbsp;") for name in abbrvnames]
#     prep = publication(bib_dir / "prep.bib", names=html_names, label="P")
#     jrnl = publication(bib_dir / "jrnl.bib", names=html_names, label="J")
#     conf = publication(bib_dir / "conf.bib", names=html_names, label="C")
    
#     content = f"""
# <h1>Publications</h1>
# <h2>Preprints</h2>
# {prep}
# <hr>
# <h2>Journal Publications</h2>
# {jrnl}
# <hr>
# <h2>Conference Publications</h2>
# {conf}
# """
#     write_html(nav, content, output_dir / "publications", dev)

#     for f in content_dir.iterdir():
#         if f.is_file():
#             filename = f.stem
#             with open(f, "r") as file:
#                 content = file.read()
#             write_html(nav, content, output_dir if filename=="index" else output_dir / filename, dev)

# def nav_html(nav_items):
#     nav_html = ""
#     for name, url in nav_items.items():
#         nav_html += f'<li class="nav-item"><a class="nav-link" href="{url}">{name}</a></li>'
#     return nav_html

# def write_html(nav, content, output, dev=False):
#     with open(template_dir / "template.html") as file:
#         html = file.read()
    
#     html = html.replace("{ nav }", nav).replace("{ content }", content)
#     html = html.replace("{ base url }", "/dev/" if dev else "/")
    
#     output.mkdir(parents=True, exist_ok=True)
#     with open(output / "index.html", "w") as file:
#         file.write(html)

# def publication(f, names=[], label=""):
#     output = "temp.html"
#     run(f"{BIBTEX2HTML} -nf pdf pdf -nf youtube YouTube -nf proquest ProQuest -nf preprint preprint -q -r -s abbrv -revkeys -nodoc -nofooter -nobibsource -o {output} {f}")

#     with open(output, "r") as file:
#         result = file.read()
    
#     os.remove(output)
    
#     for name in names:
#         result = result.replace(name, f"<strong>{name}</strong>")

#     result = result.replace("[<a name", f"[{label}<a name").replace("<sup>*</sup>", "*")
#     result = result.replace("http://arxiv.org/abs/arXiv:", "https://arxiv.org/abs/")
    
#     return result

# def serve():
#     os.system(f"live-server {output_dir}")

# def commit(msg):
#     run(f"git add -A")
#     run(f"git commit -m '{msg}'")
#     run(f"git push")

# def deploy(dev=True):
#     build(dev=dev)
    
#     repo_url = "git@github.com:mit-shin-group/mit-shin-group.github.io.git"
#     branch = "gh-pages"
#     build_dir = root_dir / "build"
    
#     tmp_dir = Path("tmp_dir")
#     run(f"git clone --depth 1 --branch {branch} {repo_url} {tmp_dir}")
    
#     dst_dir = tmp_dir / ("dev" if dev else "")
    
#     for f in build_dir.iterdir():
#         if f.is_file() or f.is_dir():
#             os.replace(f, dst_dir / f.name)

#     os.chdir(tmp_dir)
#     run("git add -A")
#     run("git commit -m 'Deploy website'")
#     run(f"git push origin {branch}")
    
#     os.rmdir(tmp_dir)

# def five_news():
#     with open(root_dir / "content" / "news.html") as file:
#         news = file.read()
#     items = [item.split("</li>")[1] for item in news.split("<li>")][2:6]
#     return "<ul>" + "".join(f"<li>{item.strip()}</li>" for item in items) + "</ul>"

# def develop(*args, **kwargs):
#     # Implement file watching logic here, using watchdog
#     pass





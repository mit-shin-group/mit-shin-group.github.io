module ShinGroupIO

using LiveServer, Git, FileWatching

const root_dir = joinpath(@__DIR__, "..")
const content_dir = joinpath(root_dir, "content")
const template_dir = joinpath(root_dir, "template")
const people_dir = joinpath(root_dir, "people")
const img_dir = joinpath(root_dir, "img")
const css_dir = joinpath(root_dir, "css")
const bib_dir = joinpath(root_dir, "bib")
const ads_dir = joinpath(root_dir, "ads")
const tex_dir = joinpath(root_dir, "tex")
const output_dir = joinpath(root_dir, "build")
const extra_dir = joinpath(root_dir, "extra")

const ADS = [
    "ad1.html" 
 ]
const KEYWORDS = [
    "{ year }" => "2025",
    "{ email }" => "sushin@mit.edu",
]
const HYPERLINKS = [
    "MIT" => "https://web.mit.edu",
    "Sungho Shin" => "people",
    "Massachusetts Institute of Technology" => "https://web.mit.edu",
    "Chemical Engineering Department" => "https://cheme.mit.edu",
    "Department of Chemical Engineering" => "https://cheme.mit.edu",
    "Julia Language" => "https://julialang.org/",
    "single instruction, multiple data" => "https://en.wikipedia.org/wiki/Single_instruction,_multiple_data",
    "nonlinear program" => "https://en.wikipedia.org/wiki/Nonlinear_programming",
    "nonlinear programs" => "https://en.wikipedia.org/wiki/Nonlinear_programming",
    "nonlinear programming" => "https://en.wikipedia.org/wiki/Nonlinear_programming",
    "MadNLP" => "https://github.com/MadNLP/MadNLP.jl",
    "ExaModels" => "https://github.com/exanauts/ExaModels.jl",
    "model predictive control" => "https://en.wikipedia.org/wiki/Model_predictive_control",
    "graph theory" => "https://en.wikipedia.org/wiki/Graph_theory",
    "statistics" => "https://en.wikipedia.org/wiki/Statistics",
    "reinforcement learning" => "https://en.wikipedia.org/wiki/Reinforcement_learning",
    "GPU computing" => "https://en.wikipedia.org/wiki/Graphics_processing_unit",
    "distributed computing" => "https://en.wikipedia.org/wiki/Distributed_computing",
    "email Sungho"=> "mailto:{sushin@mit.edu}",
    "numerical linear algebra"=>"https://en.wikipedia.org/wiki/Numerical_linear_algebra",
    "algebraic modeling platforms"=>"https://en.wikipedia.org/wiki/General_algebraic_modeling_system",
    "control theory"=> "https://en.wikipedia.org/wiki/Control_theory",
    "control"=> "https://en.wikipedia.org/wiki/Control_theory",
    "mathematical optimization"=>"https://en.wikipedia.org/wiki/Mathematical_optimization",
    "numerical optimization"=>"https://en.wikipedia.org/wiki/Mathematical_optimization",
    "machine learning"=>"https://en.wikipedia.org/wiki/Machine_learning",
    "process systems engineering"=>"https://en.wikipedia.org/wiki/Systems_engineering",
    "energy systems"=>"https://en.wikipedia.org/wiki/Energy_systems",
    "exascale supercomputers"=>"https://en.wikipedia.org/wiki/Exascale_computing",
    "Aurora"=>"https://en.wikipedia.org/wiki/Aurora_(supercomputer)",
    "Summit"=>"https://en.wikipedia.org/wiki/Summit_(supercomputer)",
    "Frontier"=>"https://en.wikipedia.org/wiki/Frontier_(supercomputer)",
    "high-performance computing"=>"https://en.wikipedia.org/wiki/High_performance_computing",
    "decision-making problems"=>"https://en.wikipedia.org/wiki/Optimization_problem",
    "mathematical optimization problems"=>"https://en.wikipedia.org/wiki/Optimization_problem",
    "automatic differentiation"=>"https://en.wikipedia.org/wiki/Automatic_differentiation",
]

const WATCHDIR = [
    "build",
    "content",
    "template",
    "img",
    "css",
]
const nav_items =  [
    "Home" => "",
    "Values" => "values",
    "People" => "people",
    "Research" => "research",
    "Publications" => "publications",
    "Software" => "software",
    "Facilities" => "facilities",
    "News" => "news",
    # "Join Us!" => "positions", 
]

const abbrvnames = [
    "S. Shin"
]
const dependencies = [
    "bibtex2html",
    "pdflatex",
    "pdf2svg",
]
const bibfiles = [
    "prep", "thes", "jrnl", "conf", "tech", "invt", "pres"
]
const figfiles = [
    "fig-1",
    "fig-2",
    "fig-3",
    "fig-4",
]

const PDFLATEX = `pdflatex -halt-on-error`
const BIBTEX = `bibtex -terse`
const BIBTEX2HTML = `bibtex2html`
const PDF2SVG = `pdf2svg`

function __init__()
    for dep in dependencies
        try run(`which $dep`, stdin, devnull, stderr)
        catch e
            @error "Dependency $dep is not installed. Please install it to build the website."
            return
        end
    end    
end

function cv()
    @info "building CV"
    curdir = @__DIR__

    cd(tex_dir)
    run(`$PDFLATEX shin`, stdin, devnull, stderr)
    for f in bibfiles
        try
            run(`$BIBTEX $f`, stdin, devnull, stderr)
        catch e
        end
        
        write(
            joinpath(tex_dir, "$f.bbl"),
            replace(
                read(joinpath(tex_dir, "$f.bbl"), String),
                "S. Shin" => "{\\bf S. Shin}"
            )
        )
    end
    run(`$PDFLATEX shin`, stdin, devnull, stderr)
    run(`$PDFLATEX shin`, stdin, devnull, stderr)
    cd(curdir)
end

function extra()
    @info "building Extra"
    curdir = @__DIR__

    cd(extra_dir)
    for f in figfiles
        run(`$PDFLATEX $f`, stdin, devnull, stderr)
        run(`$PDF2SVG $f.pdf $f.svg`, stdin, devnull, stderr)
        cp(joinpath(extra_dir, "$f.svg"), joinpath(img_dir, "$f.svg"); force=true)
    end
    cd(curdir)
end

function build(; dev = false, build_cv = true, build_extra = true, clean = true)
    
    build_cv && cv()
    build_extra && extra()
    
    @info "building website"
    # setup the directory
    if clean
        rm(output_dir; recursive = true, force=true)
    end
    mkpath(output_dir)
    mkpath(joinpath(output_dir,"img"))
    mkpath(joinpath(output_dir,"css"))
    cp(joinpath(@__DIR__,"..","img"), joinpath(output_dir,"img"); force=true)
    cp(joinpath(@__DIR__,"..","css"), joinpath(output_dir,"css"); force=true)
    cp(joinpath(@__DIR__,"..","tex/shin.pdf"), joinpath(output_dir,"shin.pdf"); force=true)

    # Define the navbar items
    nav = nav_html(nav_items)

    # Write the publication.html file
    html_names = [
        replace(
            name,
            " "=>"&nbsp;"
        )
        for name in abbrvnames]

    prep = publication(joinpath(bib_dir,"prep.bib"); names = html_names, label="P")
    jrnl = publication(joinpath(bib_dir,"jrnl.bib"); names = html_names, label="J")
    conf = publication(joinpath(bib_dir,"conf.bib"); names = html_names, label="C")
    
    content = """
<h1>Publications</h1>
<h2>Preprints</h2>
$prep
<hr>
<h2>Journal Publications</h2>
$jrnl
<hr>
<h2>Conference Publications</h2>
$conf
"""
    write_html(nav, content, joinpath(output_dir,"publications"); dev)


    # Read the markdown files and convert them to HTML
    for f in readdir(content_dir) 
        file = joinpath(content_dir,f)
        filename = splitext(basename(file))[1]
        # Write the HTML to a file
        write_html(
            nav,
            read(file, String),
            filename == "index" ? output_dir : joinpath(output_dir,filename);
            dev
        )
    end
end

function nav_html(nav_items)
    # Generate the navbar HTML
    nav_html = ""
    for (name, url) in nav_items
        nav_html *= """<li class="nav-item"><a class="nav-link" href="$(url)">$(name)</a></li>"""
    end
    return nav_html
end


function write_html(nav, content, output; dev = false)
    html = replace(
        replace(
            read(joinpath(template_dir,"template.html"), String),
            "{ nav }" => nav,
            "{ content }" => content,
        ),
        "{ base url }" => dev ? "/dev/" : "/",
        "{ recent news }" => five_news(),
        "{ ads }" => join("<hr>" * read(joinpath(ads_dir,ad), String) for ad in ADS),
        KEYWORDS...,
        ("{ $a }" => "<a href=\"$b\">$a</a>" for (a,b)  in HYPERLINKS)...
    )

    mkpath(output)
    write(joinpath(output,"index.html"), html)
end

people(names) = join((_people(name) for name in names), "<br>")
function _people(name)
    bio = Markdown.html(
        Markdown.parse(
            read(joinpath(people_dir,"$name.md"), String)
        )
    )
    photo = "img/$name.jpg"
    return """
<div class="full">
  <div class="left">
    <img class="profile-picture" src=$photo alt="photo" class="img-fluid">
  </div>
  <div class="right">
    $bio
  </div>
</div>
"""
end

function publication(f; names = String[], label="")
    path = tempname()
    output = path * ".html"
    run(`$BIBTEX2HTML -nf pdf pdf -nf youtube YouTube -nf proquest ProQuest -nf preprint preprint -q -r -s abbrv -revkeys -nodoc -nofooter -nobibsource -o $path $f`)
    result = read(output, String)
    rm(output; force = true)

    
    return replace(
        result,
        (name => "<strong>$name</strong>" for name in names)...,
        "[<a name" =>"[$label<a name",
        "<sup>*</sup>" => "*",
        "http://arxiv.org/abs/arXiv:" => "https://arxiv.org/abs/",
    )
end

function serve()
    LiveServer.serve(
        dir= output_dir
    )
end

function commit(msg)
    # Commit and push the changes
    cd(@__DIR__) do
        run(`$(git()) add -A`)
        run(`$(git()) commit -m "$msg"`)
        run(`$(git()) push`)
    end

    nothing
end

function deploy(; dev = true)
    build(; dev)
    
    # Define the repository URL and the branch to deploy to
    repo_url = "git@github.com:mit-shin-group/mit-shin-group.github.io.git"
    branch = "gh-pages"

    # Define the build directory
    build_dir = joinpath(@__DIR__,"..","build")

    # Clone the repository into a temporary directory
    tmp_dir = mktempdir()
    run(`$(git()) clone --depth 1 --branch $branch $repo_url $tmp_dir`)

    dst_dir = joinpath(tmp_dir, dev ? "dev" : "")
    
    # Copy the contents of the build directory to the repository directory
    for f in readdir(build_dir, join=true)
        run(`cp -r $f $dst_dir`)
    end

    # Commit and push the changes
    cd(tmp_dir) do
        run(`$(git()) add -A`)
        run(`$(git()) commit -m "Deploy website"`)
        run(`$(git()) push origin $branch`)
    end

    # Clean up the temporary directory
    rm(tmp_dir; recursive=true)
    
    nothing
end

function five_news()
    news = read(joinpath(@__DIR__,"..","content","news.html"),String)
    items = [split(item, "</li>")[1] for item in split(news, "<li>")]
    items = strip.(items[2:min(6,length(items))])
    return """
<ul>
$(prod("<li>\n$item\n</li>\n" for item in items))</ul>
"""    
end

function develop(args...; kwargs...)
    watch_folder(root_dir) do event
        for f in event.paths
            v = relpath(splitdir(f)[1], root_dir) 
            if v in ["tex", "extra"] && splitext(f)[2] != ".tex"
                return
            end
        end
        build(args...; kwargs...)
    end
end 

end # module



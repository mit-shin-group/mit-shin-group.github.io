# ShinGroupIO

This package is used for building and deploying website [shin.mit.edu](shin.mit.edu). 

## Dependencies
Several dependencies need to be installed to use this package.
- julia
- git
- texlive
- bibtex2html
- pdf2svg

## Usage
Once all the dependencies are obtained, run the following to instantiate the package:
```shell
$ git clone git@github.com:sshin23/sshin23.github.io.git
$ cd sshin23.github.io
$ julia --project -e 'using Pkg; Pkg.instantiate()'
```

To generate the website, first enter into julia REPL:
```julia-repl
$ julia --project
```

Then, run the following command:
```julia-repl
julia> using ShinGroupIO; ShinGroupIO.build()
```

To locally host the website, run the following command in the Julia REPL and access it through `127.0.0.1:8000`:
```julia-repl
julia> ShinGroupIO.serve()
```


Finally, to deploy the built website to the deployment branch `gh-pages`, run the following command in the Julia REPL:
```julia-repl
julia> ShinGroupIO.deploy()
```

That's it! If you encounter any issues, please [report an issue](https://github.com/sshin23/sshin23.github.io/issues).

#!/usr/bin/env julia

using Printf

PWD = pwd()
BASEDIR = dirname(@__FILE__)

# compile latex
cd(BASEDIR)

open("build-cv.log", "w") do log
    run(pipeline(`pdflatex -halt-on-error shin`, stdout=log)) # compile latex
    for f in ["prep", "thes", "jrnl", "conf", "tech", "invt", "pres"] # compile bibtex
        run(pipeline(`bibtex $f`, stdout=log))
        run(`gsed -i 's/S.~Shin/{\\bf S.~Shin}/g' $f.bbl`) # bold my name
    end
    run(pipeline(`pdflatex -halt-on-error shin`, stdout=log)) # compile with bibtex
    run(pipeline(`pdflatex -halt-on-error shin`, stdout=log)) # compile again
end

cd(PWD)

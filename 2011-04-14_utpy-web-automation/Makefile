presentation.pdf: presentation.rst
	rst2beamer --codeblocks-use-pygments presentation.rst presentation.tex
	pdflatex presentation.tex
	pdflatex presentation.tex

clean:
	git clean -fX -q

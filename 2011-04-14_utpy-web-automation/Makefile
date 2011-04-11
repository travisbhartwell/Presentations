presentation.pdf: presentation.rst
	rst2beamer --codeblocks-use-pygments presentation.rst presentation.tex || exit
	pdflatex presentation.tex || exit
	pdflatex presentation.tex || exit

clean:
	git clean -fX -q

SLIDES = presentation

%.tex : %.rst
	rst2beamer --codeblocks-use-pygments $< $@

$(SLIDES).pdf : $(SLIDES).tex
	pdflatex $(SLIDES).tex
	pdflatex $(SLIDES).tex

intermediates = $(SLIDES).aux $(SLIDES).out $(SLIDES).log $(SLIDES).snm \
		$(SLIDES).tex $(SLIDES).nav $(SLIDES).toc $(SLIDES).vrb

view : $(SLIDES).pdf
	gnome-open $(SLIDES).pdf

.PHONY : clean
clean :
	-rm $(intermediates)

dist-clean: clean
	-rm $(SLIDES).pdf

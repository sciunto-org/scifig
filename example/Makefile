DIR=~/tmp
POA=po4a
POACONF=po4a.cfg

all:
	python scifig.py -d $(DIR)

pdf:
	python scifig.py --pdf -d $(DIR)

i18n:
	$(POA) -k0 $(POACONF)

clean:
	python scifig.py -c

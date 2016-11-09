#!/bin/zsh
for f in $(grep -l variants .d/*) ; do                                                                                                                      :kcrca-macbookpro2[clarity/master]:
    if find variants -name $f:t | grep -s . ; then 
	:
    else
	cat $f
	read "yn?${f}: "
	if [[ -z $yn ]]; then
	    tgt=variants/no
	else
	    tgt=variants
	fi
	cp $f $tgt/$f:t
    fi
done

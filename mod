#!/bin/zsh
l=(`find . -name "mod_$1.class" -o -name "$1_*.class"`)
if test $0 = rmmod; then
    rm $l
else
    if test $#l -eq 0; then
	echo No files
    else
	ls $l
    fi
fi

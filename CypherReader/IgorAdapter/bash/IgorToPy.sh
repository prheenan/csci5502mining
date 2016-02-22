#!/bin/bash
# courtesy of: http://redsymbol.net/articles/unofficial-bash-strict-mode/
# (helps with debugging
# set -e: immediately exit if we find a non zero
# set -u: undefined references cause errors
# set -o: single error causes full pipeline failure.
set -euo pipefail
IFS=$'\n\t'
# datestring, used in many different places...
dateStr=`date +%Y-%m-%d:%H:%M:%S`

# Description: goal of this file is to do much of the heavy lifting converting
# an igor file into a python file

# Arguments:
#### Arg 1: File name (input file)
#### Arg 2: File name (output file)

# Returns:



pReplace()
{
    # takes in
    # (1 Name of file (modified in place
    # (2 search string
    # (3 what to replace with
    ## Sed flags:
    #g: Global
    #s: substitute
    #-i : realtime works with file
    replaceStr="s/{$2}/{$3}/g"
    # double quotes: expand the variable
    echo $1
    sed -i-e "$replaceStr" "$1"
}

inFile=$1
outFile=$2
cp $inFile $outFile
# Get rid of "Static Constant"  and the like
pReplace $outFile "Static Constant " ""
pReplace $outFile "Static StrConstant " ""
# function changes
pReplace $outFile "Static Function " "def "
pReplace $outFile "End Function " ""
pReplace $outFile "EndFor " " "

# get rid of declarations
pReplace $outFile "String " ""
pReplace $outFile "Variable " ""
# get rid of makes
pReplace $outFile "Make " ""


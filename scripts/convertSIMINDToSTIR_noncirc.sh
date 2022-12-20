#! /usr/bin/env bash

if [ $# -ne 2 ]; then
    echo "USAGE: $0 filename.h00 corfile \\" 1>&2
    exit 1
fi

# find location of script, as the awk file will be there as well
scriptdir="$(dirname -- "$(readlink -f "${BASH_SOURCE}")")"

SIMINDfilename=$1
corfile=$2

# replace extension for header file
STIRfilename=${1%%.h00}.hs

coroutputfilename=COR_output.txt

# get radii values in list (avoiding final comma), outputs to COR_output.txt
awk '{printf("%s", NR == 1 ? $1*10 : ","$1*10);} END {printf("\n");}' < "$corfile" > "$coroutputfilename"


# converts lines in header to be STIR-friendly
# includes getting radii values from COR_output.txt and putting into appropriate line
awk -F:=  -f "$scriptdir/convertSIMINDToSTIR_noncirc.awk" < "$coroutputfilename" "$SIMINDfilename" > "$STIRfilename"


# could convert from DOS 2 unix
# dos2unix "$STIRfilename"

echo "Output in $STIRfilename"


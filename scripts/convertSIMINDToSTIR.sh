#! /usr/bin/env bash
cd "`dirname $0`"
if [ $# -ne 1 ]; then
    echo "USAGE: $0 filename.h00 \\" 1>&2
    exit 1
fi

# find location of script, as the awk file will be there as well
scriptdir="$(dirname -- "$(readlink -f "${BASH_SOURCE}")")"

SIMINDfilename=$1
# replace extension
STIRfilename=${1%%.h00}.hs

awk -F:=  -f "$scriptdir/convertSIMINDToSTIR.awk" < "$SIMINDfilename" > "$STIRfilename"


# could convert from DOS 2 unix
# dos2unix "$STIRfilename"

echo "Output in $STIRfilename"


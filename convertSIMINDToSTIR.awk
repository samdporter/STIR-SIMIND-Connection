{
    if (/program|patient|institution|contact|ID|exam type|detector head|number of images.energy window|time per projection|data description|total number of images|acquisition mode/)
    { print ";" $0 }
    else if (/Radius/)
    { print "Radius := " $2*10 }
    else if (/short float/)
    { print $1 ":= float" }
    else if (/image duration/)
    { print "number of time frames := 1\n" $1 "[1] := " $2 }
    else if (/number of energy windows/)
    {}
    else if (/;energy window lower level/)
    { print "number of energy windows := 1\n" "energy window lower level[1] := " $2 }
    else if (/.energy window upper level/)
    { print "energy window upper level[1] := " $2 }
    else
    { print $0 }
}

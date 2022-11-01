!INTERFILE  :=
!imaging modality := nucmed
!version of keys := 3.3
name of data file := template_sinogram.s
;data offset in bytes := 0

!GENERAL IMAGE DATA :=
!type of data := Tomographic
imagedata byte order := LITTLEENDIAN
!number format := float
!number of bytes per pixel := 4

!SPECT STUDY (General) := 
;number of dimensions := 2
;matrix axis label [2] := axial coordinate
!matrix size [2] := 64
!scaling factor (mm/pixel) [2] := 4
;matrix axis label [1] := bin coordinate
!matrix size [1] := 64
!scaling factor (mm/pixel) [1] := 4
!number of projections := 72
!extent of rotation := 360
!process status := acquired

!SPECT STUDY (acquired data) :=
!direction of rotation := CW
start angle := 180
orbit := circular
radius := 256

!END OF INTERFILE :=

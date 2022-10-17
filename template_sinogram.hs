!INTERFILE :=
!imaging modality := nucmed
;# imaging modality 2 := EMS
!originating system := simind
!version of keys := 3.3
;program author := M Ljungberg, Lund University
;program version := V7.0.1
  
!GENERAL DATA :=
;original institution := Medical Radiation Physics
;contact person := M Ljungberg
!data offset in bytes := 0
!name of data file := template_sinogram.a00
;patient name := template_sinogram
;!study ID := jaszak
;data description :=
;# Radionuclide := ja
;exam type := EMISSION
;!patient ID := SIMIND
  
!GENERAL IMAGE DATA :=
;patient orientation := head_in
;patient rotation := supine
!type of data := tomographic
study date := 2022:10:17
study time := 13:18:20
imagedata byte order := LITTLEENDIAN
;patient rotation := supine
;patient orientation := head_in
number of energy windows := 1
energy window lower level[1] :=  126.45
energy window upper level[1] :=  154.55
;!total number of images := 64
;# Image Position First image := -128.0000 -128.0000 128.0000
;# Image Orientation := 1.000 0.000 0.000 0.000 0.000 -1.000
;# Units of data (ECT) := counts
  
!SPECT STUDY (General) :=
;number of detector heads := 1
!matrix size [1] := 64
!matrix size [2] := 1
!number format := float
!number of bytes per pixel := 4
scaling factor (mm/pixel) [1] := 4.000
scaling factor (mm/pixel) [2] := 4.000
;# scaling factor (mm/pixel) [3] := 4.000
!extent of rotation := 360
!process status := acquired
!number of projections := 64
;!number of images/energy window := 64
;!time per projection (sec) := 1.000
number of time frames := 1
image duration (sec) [1] :=  64.000
maximum pixel count := 0.134
;# total counts := 1816.681
;# Center of Rotation := 33.000
  
!SPECT STUDY (acquired data) :=
orbit := circular
Radius := 150
;acquisition mode := stepped
!direction of rotation := CCW
start angle := 0.000
;#X_offset := 0.000
  
  
;# SIMIND-SPECIFIC PARAMETERS :=
;# Intrinsic FWHM for the camera := 0.360
;# Collimator := gv-lehr
;# Collimator hole diameter := 0.150
;# Collimator hole septa := 0.020
;# Collimator thickness := 3.500
;# SIMIND: Photon Energy := 140.500
;# SIMIND: Time shift := -9999.000
  
!END OF INTERFILE :=

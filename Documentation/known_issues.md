Known issues related to using STIR and SIMIND together
===============================================

To test: do density map dimensions need to be isotropic/match source map
dimensions? (indices 34, 78, 81)

To test: do pixel sizes need to be isotropic in density maps? (index 31)

To test: do pixel sizes need to be isotropic in source maps? (index
28(?))

To test: do parameters on page 1 defining source and phantom
length/width/height have any impact when simulating voxelwise data?
(indices 2, 3, 4, 5, 6, 7)

> Conclusion: Indices 2 and 5 are important for voxelwise data (3,4,6,7
can be set to zero)

To test: non-circular orbits (elliptical orbit, or orbit based on
density map –index 42, index-35 and index-56 will be relevant)

> Conclusion: For elliptical orbit, set Index-42 to define ratio between
> major and minor axes. Index-12 defines the horizontal \[z-axis
> according to SIMIND coordinate system\] radius (tested for values
> &gt;1 and between 0 and 1)
>
> Conclusion: For non-circular orbits, the SIMIND header states “orbit
> := noncircular”, but STIR understands only “orbit := Non-circular”.
> Then need to copy values from \*.cor file, multiply by 10 to convert
> to mm, and insert into “Radii := {values from \*.cor file}”
>
> Conclusion: For non-circular orbits based on density map, set Index-42
> to &lt; 0. Index-35 is important and needs to be &lt;1 for water (i.e.
> lower than the g/cm value defining the relevant border). The absolute
> value of Index-42 then adds an airgap between the defined border and
> the surface of the detector (assume this means front of collimator).
>
> Note: confirmed with Michael Ljungberg regarding Index-42 "surface of the  
> detector" in SIMIND corresponds to the shortest distance to the overall
> device (detector meaning overall device, so could be collimator surface, 
> Aluminium cover, or crystal, depending on how device is set up \[emailed RG 22/11/22\]
>
> Conclusion: Index-56 does not seem to have an effect on RoR for
> density-based orbits

> separate .awk and .sh files have been written to convert SIMIND headers 
> from non-circular orbit data to a STIR-readable version

To test: Does SIMIND require Uint16 \[0 to 65535\] or signed int 16
\[-32768 to +32767\]

To test: z-slice order (and general conversion between SIMIND's Fortran order 
{2, 1, 0} and STIR's C++ order {0, 1, 2})
> note: binary (input) data could be read in anyway

To do: RG to check where “signed integer” vs “integer” makes a
difference (one is OK for STIR, but not for SIMIND)
> Conclusion: STIR needs "signed integer" (or "unsigned integer") when defining data types, doesn't recognise "integer"

To test: check how to get directory referencing to work for all systems (currently
can get mixed up with runtime switches)

To test: is it possible to read in DICOM data directly?

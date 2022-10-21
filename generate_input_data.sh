#! /bin/sh
# This script is part of the example suite on how to run simulation.
# It generates emission and attenuation images and a template projection
# data (which will be used for forward projection).
#
# Note: these are examples only. Modify this for your own needs.
#
#  Copyright (C) 2013-2014 University College London
#  This file is part of STIR.
#
#  SPDX-License-Identifier: Apache-2.0
#
#  See STIR/LICENSE.txt for details
#      
# Author Kris Thielemans
# 

# first need to set this to the C locale, as this is what the STIR utilities use
# otherwise, awk might interpret floating point numbers incorrectly
LC_ALL=C
export LC_ALL

echo "===  make emission image"
generate_image  generate_emission_image.par
echo "===  make attenuation image"
generate_image  generate_attenuation_image.par
# Alternative to illustrate how to use the emission image a template for
# attenuation (every voxel with some non-zero emission data is set to
# attenuation of water)
# stir_math --including-first --times-scalar .096 my_atten_image.hv my_uniform_cylinder.hv

echo "=== done"
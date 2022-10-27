
'''STIR - SIMIND connection demo.
'''

import os
from pathlib import Path
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)
data_file = "template_sinogram.hs"
save_path = current_dir
attenuation = True

show_plot = True

import stir
import stirextra

import numpy as np
import glob

import matplotlib.pyplot as plt

def plot_and_save(image, fname, slice = False):
        ''' simple image plot and save function '''
        plt.subplot(111)
        if slice:
            plt.imshow(np.squeeze(stirextra.to_numpy(image))[slice])
        else:
            plt.imshow(np.squeeze(stirextra.to_numpy(image)))            
        plt.title(fname)
        plt.savefig(fname)
        plt.show()   

def main():

    # firstly let's remove all previous outputs from simind in case this has been run before
    os.system("rm output*")

    # If the sample image and uMap haven't already been generated, let's do that now
    image_path = os.path.join(current_dir, "emission_image.smi")
    if not os.path.exists(image_path):  
        print("nothing at: " + image_path)
        print("making files")
        os.system("sh " + os.path.join(current_dir, "generate_input_data.sh"))

    image = stir.FloatVoxelsOnCartesianGrid.read_from_file(os.path.join(current_dir, "emission_image.hv")) 

    if show_plot:
        # let's have a loook at out ground truth image
        slice = image.get_lengths()[1]//2 # middle slice
        plot_and_save(image, "ground_truth", slice = slice)

    # Now we'll add an attenuation image
    if not attenuation:
        att_simind = image.get_empty_copy() # zero density map to investigate the effects on SIMIND reconstruction
    else:
        att_STIR = stir.FloatVoxelsOnCartesianGrid.read_from_file(os.path.join(current_dir, "attenuation_image.hv"))
        att_simind = att_STIR.get_empty_copy()
        att_simind.fill((stirextra.to_numpy(att_STIR)/0.15*1000).flat) # put our attenuation image in simind's units of density

    att_simind.write_to_file("attenuation_image_simind.dmi") # and save to file

    ### now some bash commands ###
    # The following bash command defines a .smc file `input.smc` follwed by a prefix for output files `output` \
    # Switches are then used to define:
    #    * /NN: a multiplier for the number of histories per projection (which is calculated using the sum of all voxel values)
    #    * /PX: defines the image pixel size in the i,j direction (transverse in this case) - im.voxel_sizes()
    #    * /FS: defines the prefix for the .smi emission image file
    #    * /FD: defines the prefix for rhe .dmi attenuation image file
    
    os.system("simind input.smc output/NN:0.1/PX:0.4/FS:emission_image.smi/FD:attenuation_image_simind.dmi")

    # And (assuming the preious cell ran) we have now simulated our SPECT data!
    # Next we need to get this data into a format the SIRF will recognise. 
    # Luckily we have a script ready that does this for us.
    # This script changes a few lines in the data's header file and the header file suffix. 
    # Differences between the conventions of interfiles in SIMIND and STIR/SIRF can be found in Rebecca's notes.

    os.system("sh " + os.path.join(current_dir , "convertSIMINDToSTIR.sh") + " output.h00")

    # And we can now create STIR projection data 
    simulated_data =  stir.ProjData.read_from_file("output.hs")

    if show_plot:
        slice = simulated_data.get_num_sinograms()//2
        # The sinogram looks like this
        plot_and_save(simulated_data, "simulated_data", slice = slice)

    ### We now use this simulated data to make a rough reconstruction using back projection

    acq_model_matrix = stir.ProjMatrixByBinSPECTUB() # create a SPECT porjection matrix object
    acq_model_matrix.set_keep_all_views_in_cache(True) # This keeps views in memory for a speed improvement
    acq_model_matrix.set_resolution_model(0.1,0.1) # Set a resolution model (just a guess!)
    if attenuation:
        acq_model_matrix.set_attenuation_image_sptr(att_STIR) # set our attenuation model in units of cm^{-1}
    acq_model_matrix.set_up(simulated_data.get_proj_data_info(), image) 

    target = image.get_empty_copy() # create an empty target image (STIR will add on top of non-empty images)

    backprojector = stir.BackProjectorByBinUsingProjMatrixByBin(acq_model_matrix) # create a backprojector object using the matrix above
    backprojector.set_up(simulated_data.get_proj_data_info(), target)

    backprojector.back_project(target, simulated_data) # And now backproject our data into the target image

    if show_plot:
        # Let's see what this looks like!
        slice = target.get_lengths()[1]//2 # middle slice
        plot_and_save(target, "backprojected_image", slice = slice)

main()

for f in glob.glob(("./tmp*")):
    os.remove(f)

print('\n=== done with %s' % __file__)
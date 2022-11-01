
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
    if attenuation:
        att_STIR = stir.FloatVoxelsOnCartesianGrid.read_from_file(os.path.join(current_dir, "attenuation_image.hv"))
        att_simind = att_STIR.get_empty_copy()
        att_simind.fill((stirextra.to_numpy(att_STIR)/0.096*1000).flat) # put our attenuation image in simind's units of density
    else:
        att_simind = image.get_empty_copy() 
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
    simind_projdata =  stir.ProjData.read_from_file("output.hs")

    if show_plot:
        slice = simind_projdata.get_num_sinograms()//2
        # The sinogram looks like this
        plot_and_save(simind_projdata, "simind_projdata", slice = slice)

    ### We now use this simulated data to make a rough reconstruction using back projection

    acq_model_matrix = stir.ProjMatrixByBinSPECTUB() # create a SPECT porjection matrix object
    acq_model_matrix.set_keep_all_views_in_cache(False) # This keeps views in memory for a speed improvement
    acq_model_matrix.set_resolution_model(0.1,0.1) # Set a resolution model (just a guess!)
    if attenuation:
        acq_model_matrix.set_attenuation_image_sptr(att_STIR) # set our attenuation model in units of cm^{-1}
    acq_model_matrix.set_up(simind_projdata.get_proj_data_info(), image) 

    target = image.get_empty_copy() # create an empty target image (STIR will add on top of non-empty images)

    ### we now want to do something with this data. First we create a STIR forward and back projector pair
    projector = stir.ProjectorByBinPairUsingProjMatrixByBin(acq_model_matrix)
    projector.set_up(simind_projdata.get_proj_data_info(), image)

    projector.get_back_projector().back_project(target, simind_projdata) # And now backproject our data into the target image

    if show_plot:
        # Let's see what this looks like!
        slice = target.get_lengths()[1]//2 # middle slice
        plot_and_save(target, "backprojected_image", slice = slice)

    ### How does simlauted data compare to a STIR forward projection?
    
    stir_projdata = stir.ProjDataInMemory(simind_projdata.get_exam_info(),
                                    simind_projdata.get_proj_data_info())
    
    projector.get_forward_projector().forward_project(stir_projdata, image)
    
    if show_plot:
        slice = stir_projdata.get_num_sinograms()//2
        # The sinogram looks like this
        plot_and_save(stir_projdata, "stir_projdata", slice = slice)
        
    ### Now let's reconstruct this using OSEM ###
    
    # create our objective function
    obj_function = stir.PoissonLogLikelihoodWithLinearModelForMeanAndProjData3DFloat()
    obj_function.set_proj_data_sptr(simind_projdata)
    obj_function.set_projector_pair_sptr(projector)
    
    # and now our reconstruction object
    recon = stir.OSMAPOSLReconstruction3DFloat()
    recon.set_objective_function(obj_function)
    recon.set_num_subsets(2)
    recon.set_num_subiterations(4)
    recon.set_max_num_full_iterations(4)
    
    # create a dummy image to fill with out reconstructed image
    target = image.get_empty_copy()
    target.fill(1)

    # and reconstruct
    recon.set_up(target)
    s = recon.reconstruct(target)
    print(s) # This will tell us if the recontruction has been helpful
    
    if show_plot:
        slice = stir_projdata.get_num_sinograms()//2
    # The recpnstructed image
    plot_and_save((target), "reconstructed_image", slice = slice)

main()

for f in glob.glob(("./tmp*")):
    os.remove(f)

print('\n=== done with %s' % __file__)
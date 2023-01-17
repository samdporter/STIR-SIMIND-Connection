
'''STIR - SIMIND connection demo.

Usage:
  STIR_simind [--help | options]
  
Options:
  -f <file>, --file=<file>              raw data file [default: template_sinogram.hs]
  -p <path>, --path=<path>              path to data files, defaults to current directory
  -s <save>, --save=<save>              path to save files, defaults to current directory
  -a <attn>, --attenuation=<attn>       whether to use attenuation in reconstruction & simulation. True or False.  [default: True]
  --non-interactive                     do not show plots
'''

__version__ = '0.0.1'

from docopt import docopt

import os

import stir
import stirextra

import numpy as np
import glob
import os
import subprocess
from pathlib import Path # for creating directories
import shutil # for copying files

import matplotlib.pyplot as plt

import platform

current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)

current_os = platform.system().lower()

parent_dir = Path(current_dir).parent.absolute()

output_dir = os.path.join(parent_dir, 'output_files')

subprocess.run(["mkdir", "-p", output_dir])

def plot_show_save(image, fname, save_dir, slice = False):
        ''' simple image plot and save function '''
        plt.subplot(111)
        if slice:
            plt.imshow(np.squeeze(stirextra.to_numpy(image))[slice])
        else:
            plt.imshow(np.squeeze(stirextra.to_numpy(image)))            
        plt.title(fname)
        plt.savefig(os.path.join(save_dir, fname))
        plt.show()   
        image.write_to_file(os.path.join(save_dir, fname))

def to_projdata(numpy_array, proj_data_info, exam_info):
    ''' get STIR projection data from numpy array'''
    projdataout=stir.ProjDataInMemory(exam_info, proj_data_info)
    projdataout.fill(numpy_array.flat)
    return projdataout

def main(args):
    
    data_file = args['--file']
    if data_file is None:
        data_file = "template_sinogram.hs"

    data_path = args['--path']
    if data_path is None:
        data_path = current_dir

    save_path = args['--save']
    if save_path is None:
        save_path = current_dir

    if args['--attenuation'] == 'False':
        attenuation = False
    else:
        attenuation = True

    show_plot = not args['--non-interactive']

    # let's generate some data
    generate_data = os.path.join(Path(current_dir).parent.absolute(), 'scripts', 'generate_input_data.sh')
    if Path(generate_data).exists():
        subprocess.run(["sh", generate_data, current_os])
    else:
        print('generate_input_data.sh not found')

    image = stir.FloatVoxelsOnCartesianGrid.read_from_file(os.path.join(current_dir, "emission_image.hv")) 

    if show_plot:
        # let's have a loook at out ground truth image
        slice = image.get_lengths()[1]//2 # middle slice
        plot_show_save(image, "ground_truth", output_dir, slice = slice)

    # Now we'll add an attenuation image
    if attenuation:
        att_STIR = stir.FloatVoxelsOnCartesianGrid.read_from_file(os.path.join(current_dir, "attenuation_image.hv"))
        att_simind = att_STIR.get_empty_copy()
        att_simind.fill((stirextra.to_numpy(att_STIR)/0.096*1000).flat) # put our attenuation image in simind's units of density
    else:
        att_simind = image.get_empty_copy() 
    att_simind.write_to_file("attenuation_image_simind.dmi") # and save to file
    
    if show_plot:
        slice = att_simind.get_lengths()[1]//2 # middle slice
        # The sinogram looks like this
        plot_show_save(att_simind, "attenuation_image", output_dir, slice = slice)
        
    src = os.path.join(Path(current_dir).parent.absolute(),"input_files")
    
    for (root, dirs, files) in os.walk(src):
        for f in files:
            if not os.path.exists(os.path.join(current_dir,"symlink_"+f)):
                os.symlink(os.path.join(src,f), os.path.join(current_dir,"symlink_"+f))
                print("symlink @ " + os.path.join(src,"symlink_"+f))
            else: print("symlink already exists")

    ### now some bash commands ###
    # The following bash command defines a .smc file `input.smc` follwed by a prefix for output files `output` \
    # Switches are then used to define:
    #    * /NN: a multiplier for the number of histories per projection (which is calculated using the sum of all voxel values)
    #    * /PX: defines the image pixel size in the i,j direction (transverse in this case) - im.voxel_sizes()
    #    * /FS: defines the prefix for the .smi emission image file
    #    * /FD: defines the prefix for rhe .dmi attenuation image file
    

    subprocess.run(["simind", "symlink_input", "output" ,"/NN:.01", "/PX:0.4", 
                    "/FS:emission_image.smi", "/FD:attenuation_image.dmi"])

    # And (assuming the preious cell ran) we have now simulated our SPECT data!
    # Next we need to get this data into a format the SIRF will recognise. 
    # Luckily we have a script ready that does this for us.
    # This script changes a few lines in the data's header file and the header file suffix. 
    # Differences between the conventions of interfiles in SIMIND and STIR/SIRF can be found in Rebecca's notes.

    subprocess.run(["sh", os.path.join("..", "scripts", "convertSIMINDToSTIR.sh"), 
                    os.path.join(current_dir, "output_tot_w1.h00")])

    # And we can now create STIR projection data 
    simind_projdata_flipped =  stir.ProjData.read_from_file("output_tot_w1.hs")
    projdata_arr = stirextra.to_numpy(simind_projdata_flipped)

    simind_projdata = to_projdata(projdata_arr, simind_projdata_flipped.get_proj_data_info(),
                simind_projdata_flipped.get_exam_info())

    if show_plot:
        slice = simind_projdata.get_num_sinograms()//2
        # The sinogram looks like this
        plot_show_save(simind_projdata, "simind_projdata", output_dir, slice = slice)

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

    #projector.get_back_projector.back_project()

    ### How does simlauted data compare to a STIR forward projection?
    
    stir_projdata = stir.ProjDataInMemory(simind_projdata.get_exam_info(),
                                    simind_projdata.get_proj_data_info())
    
    projector.get_forward_projector().forward_project(stir_projdata, image)
    
    if show_plot:
        slice = stir_projdata.get_num_sinograms()//2
        # The sinogram looks like this
        plot_show_save(stir_projdata, "stir_projdata", output_dir, slice = slice)
        
    ### Now let's reconstruct this using OSEM ###
    
    # create our objective function
    obj_function = stir.PoissonLogLikelihoodWithLinearModelForMeanAndProjData3DFloat()
    obj_function.set_proj_data_sptr(simind_projdata)
    obj_function.set_projector_pair_sptr(projector)
    
    # and now our reconstruction object
    recon = stir.OSMAPOSLReconstruction3DFloat()
    recon.set_objective_function(obj_function)
    recon.set_num_subsets(9)
    recon.set_num_subiterations(9)
    recon.set_max_num_full_iterations(1)
    recon.set_disable_output(True)
    
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
    plot_show_save((target), "reconstructed_image", output_dir, slice = slice)
    
    # unlink all symlinks
    for (root, dirs, files) in os.walk(src):
        for f in files:
            if os.path.exists(os.path.join(current_dir,"symlink_"+f)):
                os.unlink(os.path.join(current_dir,"symlink_"+f))
    
    # move output files to output directory
    for (root, dirs, files) in os.walk(current_dir):
        for f in files:
            if f.startswith("output"):
                shutil.move(os.path.join(current_dir,f), os.path.join(output_dir,f))
    
args = docopt(__doc__, version=__version__)
main(args)
    
for f in glob.glob(("./tmp*")):
    os.remove(f)

print('\n=== done with %s' % __file__)
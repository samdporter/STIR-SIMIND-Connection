
'''STIR - SIMIND connection demo.
'''

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
data_file = "template_sinogram.hs"
data_path = os.path.dirname(os.path.realpath(__file__))
save_path = data_path
attenuation = True

save = False

show_plot = True

import stir
import stirextra

import numpy as np
import glob

import matplotlib.pyplot as plt

def create_sample_image(image):
    '''fill the image with some geometric shapes to create a simple phantom image'''
    im_shape = image.shape()
    tmp_im = image.get_empty_copy()
    
    shapeim = tmp_im.get_empty_copy()
    
    # create a body-like ellipsoid shape
    shape = stir.EllipsoidalCylinder()
    shape.set_length(400)
    shape.set_radius_x(im_shape[2]//2*3)
    shape.set_radius_y(im_shape[1]//3*4)
    shape.scale = (150)
    shape.set_origin((stir.FloatCartesianCoordinate3D(0,0,0)))
    shape.construct_volume(shapeim, stir.IntCartesianCoordinate3D(1,1,1))
    tmp_im.xapyb(tmp_im,1,shapeim,1)

    # add some lung-like shapes shape
    shape.set_radius_x(im_shape[2]//2)
    shape.set_radius_y(im_shape[1])
    shape.set_origin((stir.FloatCartesianCoordinate3D(0,0,-im_shape[2]//3*2)))
    shape.construct_volume(shapeim, stir.IntCartesianCoordinate3D(1,1,1))
    tmp_im.xapyb(tmp_im,1,shapeim,-0.5)

    shape.set_origin((stir.FloatCartesianCoordinate3D(0,0, im_shape[2]//3*2)))
    shape.construct_volume(shapeim, stir.IntCartesianCoordinate3D(1,1,1))
    tmp_im.xapyb(tmp_im,1,shapeim,-0.5)

    # a spine-like shape
    shape.set_radius_x(im_shape[2]//4)
    shape.set_radius_y(im_shape[1]//4)
    shape.set_origin((stir.FloatCartesianCoordinate3D(0, im_shape[1]//5*4, 0)))
    shape.construct_volume(shapeim, stir.IntCartesianCoordinate3D(1,1,1))
    tmp_im.xapyb(tmp_im,1,shapeim,0.5)

    return tmp_im

def main():

    templ_sino = stir.ProjData.read_from_file(os.path.join(data_path, data_file)) # template sirf acquisition data

    image = stir.FloatVoxelsOnCartesianGrid(templ_sino.get_proj_data_info(), 1)
    image = stir.zoom_image(create_sample_image(image), 1, 0, 0, 64) # use the template to create an empty image

    if show_plot:
        plt.figure()
        plt.subplot(111)
        plt.imshow(np.squeeze(stirextra.to_numpy(image)))
        plt.title('Simulated Sinogram')
        plt.show()

    if attenuation:
        att_SIMIND = image.get_empty_copy()
        att_SIMIND.fill((stirextra.to_numpy(image)/0.15).flat) # approximate density image used in SIMIND (mg/cm^3)
        # att_STIR = image.get_empty_copy()
        # att_STIR.fill((stirextra.to_numpy(image)/1000).flat) # approximate attenuation coefficient image used in STIR (/cm)
    
    else:
        att_SIMIND = image.get_empty_copy() # zero density map to investigate the effects on SIMIND reconstruction

    if save:
        image.write_to_file(os.path.join(save_path, "image.smi"))
        #att_STIR.write_to_file(os.path.join(save_path, "attenuation_stir.hv"))
        att_SIMIND.write_to_file(os.path.join(save_path, "./attenuation_simind.dmi"))

    os.system("simind input output/NN:0.001/PX:0.4/FS:image.smi/FD:attenuation_simind.dmi")

    os.system("sh convertSIMINDToSTIR.sh output.h00")

    simulated_data =  stir.ProjData.read_from_file("output.hs")

    if show_plot:
        plt.figure()
        plt.subplot(111)
        plt.imshow(np.squeeze(stirextra.to_numpy(simulated_data)))
        plt.title('Simulated Sinogram')
        plt.show()

    return 0

main()

for f in glob.glob(("./tmp*")):
    os.remove(f)

print('\n=== done with %s' % __file__)
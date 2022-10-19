'''SIRF - SIMIND connection demo.
'''

import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
data_file = "template_sinogram.hs"
data_path = os.path.dirname(os.path.realpath(__file__))
save_path = data_path
attenuation = True

save = False

show_plot = True

# import sirf
import sirf.STIR as STIR
import glob

msg = STIR.MessageRedirector("info.txt", "warnings.txt", "error.txt") # redirects error, information and warning messages to file

def crop_image(templ_sino, image, nx, ny, nz, slice = None):
    """Crop ImageData from (vol_z,vol_y,vol_x) to (nz,ny,nx)"""
    vol = image.as_array()
    vol_dims = vol.shape
    x_origin = vol_dims[2]//2
    y_origin = vol_dims[1]//2
    if slice is None:
        z_origin = vol_dims[0]//2
    else:
        z_origin = slice
    
    vol = vol[z_origin-nz//2:z_origin+nz//2+nz%2,y_origin-ny//2:y_origin+ny//
              2+ny%2,x_origin-nx//2:x_origin+nx//2+nx%2]
    image = STIR.ImageData(templ_sino)
    dim=(nz,ny,nx)
    vol = vol.reshape(dim)
    voxel_size=image.voxel_sizes()
    image.initialise(dim,voxel_size)
    image.fill(vol)

def create_sample_image(image):
    '''fill the image with some geometric shapes to create a simple phantom image'''
    im_shape = image.shape
    image.fill(0)
    
    # create a body-like ellipsoid shape
    shape = STIR.EllipticCylinder()
    shape.set_length(400)
    shape.set_radii((im_shape[1]//3*4, im_shape[2]//2*3))
    shape.set_origin((0, 0, 0))

    # add the shape to the image
    image.add_shape(shape, scale = 150)

    # add some lung-like shapes shape
    shape.set_radii((im_shape[1], im_shape[2]//2))
    shape.set_origin((0,0, -im_shape[2]//3*2))
    image.add_shape(shape, scale = -75)

    shape.set_origin((0, 0, im_shape[2]//3*2))
    image.add_shape(shape, scale = -75)

    # a spine-like shape
    shape.set_radii((im_shape[1]//4, im_shape[2]//4))
    shape.set_origin((0, im_shape[1]//5*4, 0))
    image.add_shape(shape, scale = 75)

    # and a lung tumour-like shape
    shape.set_radii((im_shape[1]//5, im_shape[2]//5))
    shape.set_origin((0, -im_shape[1]//5, im_shape[2]//2))
    image.add_shape(shape, scale = 100)
    

def main():
    templ_sino = STIR.AcquisitionData("./template_sinogram.hs") # template sirf acquisition data

    image =  templ_sino.create_uniform_image(0)
    create_sample_image(image) # use the template to create an empty image

    ### I'm currently unsure why this is necessary. It requires further investigastion ###
    crop_image(templ_sino, image, templ_sino.dimensions()[3], templ_sino.dimensions()[2], templ_sino.dimensions()[1])

    image = image.zoom_image((0.5,1,1)) # zoom the image along the z axis. This line is required because SIRF was originally set up for PET data with a 180 degree acquisition
    if attenuation:
        att_STIR = image/1000 # approximate attenuation coefficient image used in STIR (/cm)
        att_SIMIND = att_STIR/0.15*1000 # approximate density image used in SIMIND (mg/cm^3)
    else:
        att_SIMIND = image.get_uniform_copy(0) # zero density map to investigate the effects on SIMIND reconstruction

    if show_plot:
        image.show()

    os.system("simind input output/NN:0.001/PX:0.4/FS:image/FD:attenuation_simind")

    os.system("sh convertSIMINDToSTIR.sh output.h00")

    simulated_data = STIR.AcquisitionData("output.hs")
    simulated_data.show()   

    acq_model_matrix = STIR.SPECTUBMatrix()
    acq_model_matrix.set_attenuation_image(att_STIR) # set the attenuation image for reconstruction 
    acq_model_matrix.set_resolution_model(0.1,0.1,full_3D=False) # where we have defnied our collimator blurring as a gaussian with SD 0.1mm and a collimator slope of 0.1mm

    am = STIR.AcquisitionModelUsingMatrix(acq_model_matrix)
    am.set_up(simulated_data, image)

    res = am.backward(simulated_data)

    if show_plot:
        res.show()


main()

for f in glob.glob(("./tmp*")):
    os.remove(f)

print('\n=== done with %s' % __file__)
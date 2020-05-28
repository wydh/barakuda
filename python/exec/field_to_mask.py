#!/usr/bin/env python

#       B a r a K u d a
#
#       L. Brodeau, 2017]

import sys
import numpy as nmp
import string
import os
from netCDF4 import Dataset

l_fake_coor = True
#l_fake_coor = False

l_nemo_like = False

narg = len(sys.argv)
if narg not in [3]:
    print 'Usage: '+sys.argv[0]+' <netcdf_file.nc> <3D netcdf_variable>'; sys.exit(0)

cf_nc = sys.argv[1]
cv_nc = sys.argv[2]
#ciext = sys.argv[3]

    
cfname, cncext = os.path.splitext(cf_nc)


cf_msk = string.replace(os.path.basename(cf_nc), cv_nc, 'mask')

print ' *** Will create mask '+cf_msk






# Reading data array:
f_nc = Dataset(cf_nc)
Ndim = len(f_nc.variables[cv_nc].dimensions)
rfill_val = f_nc.variables[cv_nc]._FillValue
print ' *** rfill_val =',rfill_val
#
if   Ndim == 4:
    xfield = f_nc.variables[cv_nc][0,:,:,:]
elif Ndim == 3:
    xfield = f_nc.variables[cv_nc][:,:,:]
    #elif Ndim == 2:
    #    xfield = f_nc.variables[cv_nc][:,:]
else:
    print ' ERROR (mk_zonal_average.py) => weird shape for your mask array!'
    sys.exit(0)
#xfield  = f_nc.variables[cv_nc][:,:]
f_nc.close()



(nz,ny,nx) = nmp.shape(xfield)

print xfield[0,:,:]

print("nx, ny, nz =",nx,ny,nz)


mask = nmp.zeros((nz,ny,nx))

if rfill_val > 0:
    idd = nmp.where( xfield < rfill_val )
else:
    idd = nmp.where( xfield > rfill_val )
mask[idd]=1



f_out = Dataset(cf_msk, 'w', format='NETCDF4')

# Dimensions:
cdim_x = 'longitude'
cdim_y = 'latitude'
cdim_z = 'depth'
if l_nemo_like:
    cdim_x = 'x'
    cdim_y = 'y'
    cdim_z = 'z'

f_out.createDimension(cdim_x, nx)
f_out.createDimension(cdim_y, ny)
f_out.createDimension(cdim_z, nz)


#if l_fake_coor:
#    id_lon  = f_out.createVariable('lon0','f4',(cdim_x,))
#    id_lat  = f_out.createVariable('lat0','f4',(cdim_y,))
#    id_lon[:] = vlon[:]
#    id_lat[:] = vlat[:]



id_msk  = f_out.createVariable('mask','i1',(cdim_z,cdim_y,cdim_x,))
id_msk.long_name = 'Land-Sea mask'
id_msk[:,:,:]   = mask[:,:,:]


f_out.About  = 'Variable '+cv_nc+' converted to a mask...'
f_out.Author = 'Generated with image_to_netcdf.py of BARAKUDA (https://github.com/brodeau/barakuda)'

f_out.close()



print cf_msk+' created!!!'

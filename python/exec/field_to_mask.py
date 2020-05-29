#!/usr/bin/env python

#       B a r a K u d a
#
#       L. Brodeau, 2017]

import sys
import numpy as nmp
import string
import os
from netCDF4 import Dataset

#l_fake_coor = True
#l_fake_coor = False

l_use_fillval = True

narg = len(sys.argv)
if narg not in [3,4]:
    print 'Usage: '+sys.argv[0]+' <netcdf_file.nc> <2D or 3D netCDF field> (<value>)'
    print '  => if no <value> is specified: the "_FillValue" attribute is used!\n'
    sys.exit(0)

cf_nc = sys.argv[1]
cv_nc = sys.argv[2]

if narg == 4:
    l_use_fillval = False
    rfill_val = float(sys.argv[3])
    
cfname, cncext = os.path.splitext(cf_nc)


#cf_msk = 'lsm_'+string.replace(os.path.basename(cf_nc), cv_nc, 'mask')

cf_msk = 'mask.nc'

print ' *** Will create mask '+cf_msk






# Reading data array:
f_nc = Dataset(cf_nc)
ndim = len(f_nc.variables[cv_nc].dimensions)
#
if l_use_fillval:
    list_att_var = f_nc.variables[cv_nc].ncattrs()
    if '_FillValue' in list_att_var:
        rfill_val = f_nc.variables[cv_nc]._FillValue
    elif 'missing_value' in list_att_var:
        rfill_val = f_nc.variables[cv_nc].missing_value
    else:
        print 'ERROR: found neither "_FillValue" nor "missing_value" attribute for variable '+cv_nc+' !'; sys.exit(0)
        #
print '\n *** Field value to use to generate mask: rfill_val =',rfill_val,'\n'
#
# Looking at the dimmensions of the variable:
list_dim_var = f_nc.dimensions.keys()
print 'list_dim_var = ', list_dim_var
# Check if one is unlimited:
inu = 0
for cd in list_dim_var:
    if f_nc.dimensions[cd].isunlimited(): inu = inu + 1
if inu > 1:
    print 'PROBLEM: there are more than one UNLIMITED dimension in the file!'
    sys.exit(0)

NbDim = 3
#
if   ndim == 4:
        xfield = f_nc.variables[cv_nc][0,:,:,:] # 3D !       BAD!
elif ndim == 3:
    if inu==1:
        xfield = f_nc.variables[cv_nc][0,:,:] ; # 2D !
        NbDim = 2
    else:
        xfield = f_nc.variables[cv_nc][:,:,:] ; # 3D !       
elif ndim == 2:
        if inu==0:
            xfield = f_nc.variables[cv_nc][:,:]
            NbDim = 2
        else:
            print 'PROBLEM: your field does not seem to be 3D!'
else:
    print ' ERROR (mk_zonal_average.py) => weird shape for your mask array!'
    sys.exit(0)
#xfield  = f_nc.variables[cv_nc][:,:]
f_nc.close()


nz = -1
if NbDim==3:
    (nz,ny,nx) = nmp.shape(xfield)
    print("nx, ny, nz =",nx,ny,nz)
    mask = nmp.zeros((nz,ny,nx))
else:
    (ny,nx) = nmp.shape(xfield)
    print("nx, ny =",nx,ny)
    mask = nmp.zeros((ny,nx))



if rfill_val > 0:
    idd = nmp.where( xfield < rfill_val )
else:
    idd = nmp.where( xfield > rfill_val )
mask[idd]=1



f_out = Dataset(cf_msk, 'w', format='NETCDF4')

# Dimensions:
cdim_x = 'x'
cdim_y = 'y'
cdim_z = 'z'

f_out.createDimension(cdim_x, nx)
f_out.createDimension(cdim_y, ny)
if NbDim==3: f_out.createDimension(cdim_z, nz)


#if l_fake_coor:
#    id_lon  = f_out.createVariable('lon0','f4',(cdim_x,))
#    id_lat  = f_out.createVariable('lat0','f4',(cdim_y,))
#    id_lon[:] = vlon[:]
#    id_lat[:] = vlat[:]


if NbDim==3:
    id_msk  = f_out.createVariable('mask','i1',(cdim_z,cdim_y,cdim_x,))
    id_msk[:,:,:]   = mask[:,:,:]
else:
    id_msk  = f_out.createVariable('mask','i1',(cdim_y,cdim_x,))
    id_msk[:,:]   = mask[:,:]

id_msk.long_name = 'Land-Sea mask'


f_out.About  = 'Variable '+cv_nc+' converted to a mask...'
f_out.Author = 'Generated with image_to_netcdf.py of BARAKUDA (https://github.com/brodeau/barakuda)'

f_out.close()



print cf_msk+' created!!!'

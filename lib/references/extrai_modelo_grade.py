import os
import sys
import numpy
import netCDF4
import pygrib


modelo = sys.argv[1]
arq_modelo = sys.argv[2]
arq_out_nome = sys.argv[3]


if modelo == "GFS":
    
   arq_in = Nio.open_file(arq_modelo + ".grib2")
     
   lat = arq_in.variables["lat_0"][:]
   lon = arq_in.variables["lon_0"][:]
   
   # Corrigindo lon
   lon = numpy.where( lon < 180, lon, lon - 360.)
         
   lon, lat = numpy.meshgrid( lon, lat )
   
   
   
if modelo == "WRF":
   
   arq_in = netCDF4.Dataset(arq_modelo)
   
   lat = arq_in.variables["XLAT"][0,:,:]
   lon = arq_in.variables["XLONG"][0,:,:]
   
   # Atributos globais para serem lidos no thredds
   GRIDTYPE      = getattr(arq_in, "GRIDTYPE")
   MAP_PROJ      = getattr(arq_in,"MAP_PROJ")
   CEN_LON       = getattr(arq_in,"CEN_LON")
   MAP_PROJ_CHAR = getattr(arq_in,"MAP_PROJ_CHAR")
   STAND_LON     = getattr(arq_in,"STAND_LON")
   TRUELAT1      = getattr(arq_in,"TRUELAT1")
   TRUELAT2      = getattr(arq_in,"TRUELAT2")
   CEN_LAT       = getattr(arq_in,"CEN_LAT")
   DX            = getattr(arq_in,"DX")
   DY            = getattr(arq_in,"DY")
   MOAD_CEN_LAT  = getattr(arq_in,"MOAD_CEN_LAT")
   
arq_in.close()


# Escrevendo as lat/lon
if os.path.exists( arq_out_nome ):
   os.remove( arq_out_nome )
   
   
arq_out = netCDF4.Dataset( arq_out_nome, 'w')

arq_out.createDimension("latitude", lat.shape[0])
arq_out.createDimension("longitude", lon.shape[1])

arq_out.createVariable("latitude", "f", ("latitude", "longitude"))
arq_out.createVariable("longitude", "f", ("latitude", "longitude"))
   
arq_out.variables["latitude"][:,:] = lat[:,:].astype('f')
arq_out.variables["longitude"][:,:] = lon[:,:].astype('f')
   
arq_out.variables["latitude"].units  = 'degrees_north'
arq_out.variables["longitude"].units = 'degrees_east'


if modelo == "WRF":
   
    # Atributos globais para serem lidos no thredds
    setattr(arq_out, 'GRIDTYPE',      GRIDTYPE)
    setattr(arq_out, 'MAP_PROJ',      MAP_PROJ)
    setattr(arq_out, 'CEN_LON',       CEN_LON)
    setattr(arq_out, 'MAP_PROJ_CHAR', MAP_PROJ_CHAR)
    setattr(arq_out, 'STAND_LON',     STAND_LON)
    setattr(arq_out, 'TRUELAT1',      TRUELAT1)
    setattr(arq_out, 'TRUELAT2',      TRUELAT2)
    setattr(arq_out, 'CEN_LAT',       CEN_LAT)
    setattr(arq_out, 'DX',            DX )
    setattr(arq_out, 'DY',            DY)
    setattr(arq_out, 'MOAD_CEN_LAT',  MOAD_CEN_LAT)
   
   
arq_out.close()

   



;---------------------------------------------------------------------
; Description: Creates table and map plots of selected energy budget terms 
; Usage: (THIS WILL CHANGE)
;---------------------------------------------------------------------

;load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
;load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"

begin
;---Open the WRF data file
  ;loadscript("cfs_lib_gen.ncl")
  
; ------ Load Files ---------------------------------;
  a = addfile(FNAME, "r")      ; model end file 

  ; times    = wrf_user_list_times(a)  ; get times in the file
  var = a->VARNAME(:,:)

  ; load a misc wrfout to get map things 
  a = addfile(WRF_EXAMPLE_FILE,"r")

; ------------ CREATE MAP PLOT --------------;   
;  var!0 = VARNAME
  var@units = UNITS
  ter = a->HGT(0,:,:)
  wks = gsn_open_wks("png",PLOTTITLE)
  cres = True
; Plot variable
  res = cres
  res@cnFillOn = True
  res@cnFillPalette = "BlueDarkRed18"
  ;res@ContourParameters        = (/-100,100,10/)    
  ;res@ContourParameters        = (/-100,100,10/)    
  contour_e = wrf_contour(a,wks,var,res)
  delete(res)

; Make terrain contour plot 
  res = cres
  res@cnLineLabelBackgroundColor = -1
  res@cnLevelSpacingF = 500.                      ; contour interval
  res@cnLineThicknessF = 3.0

  contour_ter = wrf_contour(a, wks, ter, res) 
  pltres = True
  mpres=True
  
  ov = wrf_map_overlays(a,wks,(/contour_e,contour_ter/),pltres,mpres)
  
;
end 

# ImportDSF-for-Blender #

This is an addon for Blender allowing to import terrain mesh of X-Plane stored in .dsf files.

*Warning:* This program is in an early stage and probly has some errors. But feedback from testers welcome.

## IMPORTANT UPDATE ##
Seems the current addon-code has some issues with imports. To fix this you would need to copy xplnedsf2.py directly into the addons folder. Alternatively use the all_in_one_script file by directly copying to a script page and run it.
However, this code retrieves terrain data from X-Plane (dsf file needs to be in a XP sub-folder) for showing terrain and might not run under XP12 (to be tested by someone owning XP12). In case of issues with XP12 because the material information is not found you could remove the two code lines adding the actual texture. They begin with "texImage.image = ..." and are in the function add_material() in file DSF_load.py. In that case you would at least see the mesh triangles.

Often dsf files are 7zipped. In order to unzip you need to have py7zlib installed in your blender python (not that easy but there are tutorials on how to install python modules in blender with pip) or just manually 7unzip the dsf file you would like to work with.

## Installation ##

1. Download this repository as zip (through GitHub this can be done through the Clone or download > Download ZIP button).

2. Run Blender and go to Edit > Preferences > Add-ons and press the Install... button.

3. Select the downloaded ZIP and press Install Add-on from File....

4. nable the add-on from the list, by ticking the empty box next to the add-on's name.

## Usage ##
In Blender go to Top-Menue File > Import > X-Plane dsf mesh.
In the file menu you select the accordin dsf file. In order that the import function will find all relevant terrain files and images to display, 
the dsf file imported should reside in a X-Plane sub folder.
On the right in the import menu you have the option to only import parts of the 1 by 1 grid dsf file. As full dsf file can be huge especially 
for smaller systems you should make use of this option in order crashing by out of memory.

## Further Development ##
I'm not using X-Plane any more so I stoppe development. For those who like, next steps could be:
* Clean and stabilize code
* Add further options for import like using Mercartor projection
* Description or menu functions for updating the mesh including all overlays
* Export to dsf file again

Any support welcome. Especially also hints from Blender exports on good methods how to update the mesh in a useful way.

# ImportDSF-for-Blender #

This is an addon for Blender allowing to import terrain mesh of X-Plane stored in .dsf files.

*Warning:* This program is in an early stage and probly has some errors. But feedback from testers welcome.

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
* Clean and stabilize code
* Add further options for import like using Mercartor projection
* Description or menu functions for updating the mesh including all overlays
* Export to dsf file again

Any support welcome. Especially also hints from Blender exports on good methods how to update the mesh in a useful way.

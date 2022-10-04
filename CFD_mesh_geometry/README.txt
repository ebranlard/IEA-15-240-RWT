# CFD mesh and geometry

The given components allow a first simplified CFD calculation.
The file 'IEA15MW_blade.igs' was created using a parametric CAD model fitted to the original blade description. Furthermore a closed wingtip was added.
The images give an overview about additional mesh components as used in a first CFD simulation.

Due to big file sizes, mesh components (pointwise) will be given seperately.

## grid setup

The mesh is split in different fully structured components using the chimera technique:
 * **Background**: Low resolution big dimension background grid
 * **Refinement**: Fine inner mesh area surrounding the rotor
 * **Blade**: Blade geometry and corresponding fine resolution blade mesh
 * **Hub**: Simplified hub design. Precone of 4deg and cylindrical blade connection included in geometry.

## Component description

 * **Background**: 272 points in radial direction
   157 points in depth
   average spacing around rotor ca. 1m
 * **Refinement**: 408 points in radial direction
   253 points in depth
   average spacing around rotor ca. 0.2m
 * **Blade**: 320 points in radial direction
   150 points in spanwise direction
   first cell hight 4e-6m
   diameter of blade mesh component is 16m
 * **Hub**: 256 points in radial direction



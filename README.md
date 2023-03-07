The **CHE**ap m**ESO**scopic **S**elective **P**lane **I**llumination **M**icroscope

aka 

# The cheesoSPIM

A $500 fluorescence light sheet microscope that you can build at home. Plus a protocol for clearing wood for use in fluorescence microscopy that you can also do at home. Design and build guide below.


### Motivation

1. How cheap could you make an AIBSOPT?

	At an old job I designed and built [this](https://github.com/AllenInstitute/AIBSOPT), a low-cost microscope for rapid 3D transmitted light and fluorescence imaging. The system was designed to do [optical projection tomography](https://en.wikipedia.org/wiki/Optical_projection_tomography) in which a series of 2D images are collected and computationally reconstructed into a 3D image of the sample. The principle and math behind the technique is identical to [computed tomography](https://www.nibib.nih.gov/science-education/science-topics/computed-tomography-ct) used in medical imaging. OPT uses visible light, not X-rays, and the sample is rotated between each image collected, where CT scanners rotate the detector around the patient. 
	
	After a few emails around the topic I was thinking on how the design could be made cheaper. One of its advantages is its cost, which is cheap for lab equipment.  But that's compared to, like, a confocal microscope and not to, say, a normal human number of dollars. Taking a closer look at the two most expensive pieces of the design - the camera and its lens - would make the most sense. OPT imaging is rarely starved for photons; a cheap(ish) USB webcam is plenty for this application. That leaves the lens.
	
	The images collected in an OPT are ideally an optical projection of the specimen onto the camera chip. The system approximates the detector on a CT scanner, in which there are no optics.  The image is an orthographic projection formed by a specimen in the path of a collimated X-ray beam.  The optical equivalent is imaging with a [telecentric lens](https://en.wikipedia.org/wiki/Telecentric_lens). These lenses are designed to form an image from a bunch of parallel rays of light.  The result is the optical orthographic projection we require.
	
	Telecentric lenses are adventageous in metrology and industrial machine vision because the size of an object does not vary with distance to the lens. Surplus lenses are available in a variety of specifications. These lenses fit a profile of unexpectedly common (thanks to industrial applications) and highly specific (so unlikely to be reused in new work) that makes them favorable for buying surplus. We can also afford to be a little flexible here on magnification and other specs. 
	
	I found an 0.5x C mount telecentric lens for $86, shipped, on eBay. 


2. Could you use a commercial motorized lens to tile a light sheet?

	Axial scanning is hard in microscopy.  It usually means moving something around precisely. Precision is always tough and tough usually means expensive.  A shortcut around expensive can sometimes be found in precision someone else paid for. That can mean surplus equipment that still works or can be repaired, or it can mean mass production where the precision is in the tooling, amorated over thousands of replicates. The best is when both happen - surplus, mass-produced, precision equipment. Consumer optical equipment is a good example of this intersection. Maybe there's a product out there already doing what we need for axial scanning?
	
	The [MesoSPIM](https://mesospim.org/) uses a pair of Nikon DSLR lenses as the objective lens in each of the mirrored excitation light paths. There those lenses are static and used because they have the appropriate focal length and field size with good field flatness for forming the excitation sheet. In the MesoSPIM a [tunable lens](https://mesospim.org/design/#) upstream from the DSLR lens is responsible for axially scanning the light sheet. DSLR lenses these days are all motorized - could that work for scanning the sheet on its own?
	
	Canon DSLR lens communication [documentation or at least hacked versions thereof](https://web.media.mit.edu/~bandy/invariant/move_lens.pdf) is available and works through an Arduino. Lenses using the EF protocol are a little outdated electronically but the optics still work just the same. A lens with about a 50 mm focal length is probably right, and a zoom wouldn't hurt for testing. The EF protocol is a requirement but there are something like 100 million of that type lens in the world.  
	
	I found a Canon 35mm - 105mm f4.5 EF zoom lens for $36 on eBay. 


3. Dramatic dichroics

	If the telecentric lens is the collection side and the DSLR lens is the excitation side, then this is a fluorescence imaging system. The remaining piece is how to separate the excitation light from the laser from the emitted fluorescence from a specimen. In a typical fluorescence microscope this is done with dichroic mirrors and interference filters. Here I'd need one large enough to cover the front element of the telecentric lens - 50 mm or so - which could mean upwards of $1000 from a scientific optical filter supplier for a single part. But they're not the only ones that sell dichroics! The film and stage lighting industries use interference filters for plenty. Would any of those work?
	
	Rosco's [Permacolor](https://us.rosco.com/en/products/catalog/permacolor) line has many options for colors (aka pass bands) of filter to choose from. Spectra are a little tricky to find but the Industrial Green P1086 looked to line up with GFP or FITC emission reasonably well. A good place to start. 
	
	I ordered 2 x 1.95" P1086 filters from Musson Theatrical for $70, shipped.

4. Home clearing

	A microscope needs a specimen. Fluorescence microscopy and OPT both greatly benefit from an optically clear specimen.  Makes sense if you want to see all the way through something it's easier if it's see-through. Unfortunately most of the options for tissue clearning involve a system of witches brews and potions and incantations that are stinky, sticky, sickening, or all three. 
	
	This unsanctioned project began to coalesce into an overheated science fair project and seemed appropriate to include a specimen that could be prepared at home. The item should be reasonably easy to obtain from a commercial source and clear with (reasonably) safe protocols. Turns out [cleared](https://www.youtube.com/watch?v=uUU3jW7Y9Ak) [wood](https://pubs.acs.org/doi/10.1021/acs.biomac.6b00145) is a thing as a bio-friendly building material. There the process is delignification (bleaching) followed by impregnation with plastic (index matching). 
	
	Starting with balsa wood, bleaching, and index matching with a proper solvent or mixture seemed like a reasonable way to go. This omits the impregnation step above for the more typical approach in fluorescence microscopy of soaking the bleached and delipidated specimen in an index-matching fluid. 
	Chemicals required are avialable for < $100 in quantities between sufficient and 'lifetime supply' from Amazon. 


5. LOLs

	The completion of this project became a challenge in demonstrating a working light sheet + OPT microscope and specimen to image using what is available to the general public. Reimagining a complex machine in the cheapest terms possible is a useful exercise for a few reasons.
	
	Making something cheap is challenging. It takes little deviation from idealized theory if all of your instruments are built of nothing but the highest quality materials machined to tight tolerances. If you're pushing the limits of physics then that might be necessary.  But if you're not then it's likely cheaper and faster and easier to compromise precision and performance where it's not needed. Figuring where that is true requires attention to details of the operation of the instrument and choices made outside of the usual ones for biomedical research. 
	
	Making something cheap makes it more accessable. Scientific equipment is expensive. Making it cheaper means more folks can possibly take advantage of this technology.  The work presented here is within the domain of a well-supervised group of high school students. Or if someone wants to wipe the floor with some folks at their science fair this might do it.
	
	Making it cheap makes it more fun.  The bar for trying something that costs $20 is a lot lower than if it costs $200 or $2000. The pressure for that experiment to yield something useful is lower, too.  Making it cheap leaves more room for creativity and individuality. 

### Parts + Price
- Laser - $36, eBay
	80 mW 450 nm diode laser + controller 

- Excitation filter - $21, eBay
	450/40 BP, 15 mm diameter

 - Cylindrical lens - $8 for 5, eBay
	5 mm diameter x 11 mm length

- Excitation objective lens - $36, eBay
	Canon EF 35-105mm f4.5-5.6 autofocus Zoom lens

- Cuvette - $14, Amazon
	2" x 2" x 1/16" plates, 12 pack 

- Stage
	- Z axis and carrage - $3, PC salvage
		Extracted from surplus CD-ROM

	- Theta axis - $10, eBay
		15 mm gearhead stepper motor

- Collection lens - $86, eBay
	0.5x C-mount telecentric lens

- Camera - $68, Amazon
	ELP 16 Megapixel IMX298 USB camera

- Filters - $68, Musson Theatrical
	Rosco 1.95" round Industrial Green P1086 x 2

- Arduino - $20
	Arduino Uno

 - Power supply - $20, PC salvage
	1A, 15V variable bench power supply

- Breadboard - $0
	16" x 16" x 1/2" ApplePly or similar, salvaged

- Incidentals - $100, est
	- Laser cutting
	- 3d printing
	- Hardware
		1/4"-20 cap screws
	- Tools
		T handle hex drivers
		Brake bleeder vacuum pump

 - Specimen prep
	- Wood - $5
		3/32" balsa wood, usual stuff from the display at the art/hardware/hobby store
	- Bleach - $10, Amazon
		Sodium Chlorite, 80%. Need ~1 gram.
	- Acetone - $8, Amazon
		16 oz	
	- Benzyl alcohol - $11, Amazon
		100 mL. Get 250+ mL.
	- Uv glue - $8, Amazon
		EDSRDXS UV bonding glue

### Assembly

The laser bone connects to the filter bone
the filter bone connects to the cylindrical lens bone
the cylindrical lens bone connects to the cannon lens
and the cannon lens makes the light sheet

- Excitation optics
 
	The laser head is screwed to a laser-cut base to hold it at the chosen beam height. The mount screws are adjusted to level the beam relative to the breadboard. The excitation filter and cylindrical lens are glued into laser-cut holders held in front of the laser output with double-sided tape and wire.  The output line should remain centered at the beam height and be perpendicular to the breadboard. Adjust the cylindrical lens to achieve this. The laser assembly is placed in front of the DSLR lens (in its own laser-cut holder) such that the laser line is centered in the lens aperture. A light sheet should exit the front of the lens along the lens axis.  The beam waist of this sheet can be positioned using the zoom and focus of the DSLR lens. The cylindrical lens assembly is the correct distance from the back of the DSLR lens when the beam enters and exits the beam waist at the same angle. 

- Collection optics

	The camera is attached to the telecentric lens using the 3D printed adapter available in this [repo][HERE]. The two emission filters are stacked and held with screws to a laser-cut ring which slides over the front element of the telecentric lens. This assembly is held in a laser-cut V block assembly, shimmed to match the beam height of the light sheet and specimen. The axis of the telecentric lens should be perpendicular to that of the light sheet and excitation optics.

- Stage philosophy and practice

	Every axis that moves makes things more complicated. Every axis that moves can and will move.  These moves need to be aligned. These moves need to be controlled. Every axis you can cut from your design is more simplicity and reliability you are adding.
	
	For an OPT, only the rotational axis is required. Full 3d isotropic reconstructions are generated with just rotation around the specimen axis. Here that is accomplished with a small gearhead stepper motor directly to the shaft of which the specimen is glued. This motor is small enough to be driven by the Arduino directly in response to serial commands from the PC.
	
	A light sheet microscope typically has a Z axis for specimen scanning. Here the slide from a salvaged CD-ROM drive tray is used to position the specimen and theta motor along the optical axis of the telecentric lens. Motion along this axis scans the specimen through the image plane. In the current implementation this is done manually, but a motorized version would be straightforward. The slide assembly is mounted at a 45 degree angle to the breadboard to allow for more access under the stage. 

- Breadboard and clamps

	The breadboard is made from 1/2" plywood with drilled and tapped holes for 1/4"-20 screws on a 1" grid. The wood is sealed with several layers of water-based polyurethane sanded smooth. Components are screwed directly to the breadboard using 1/4"-20 cap head screws or with strap clamps. These clamps are laser cut from 1/4" acrylic.  One screw goes in the hole; this screw should be longer than the height of the object to clamp. The other screw goes through the slot into the breadboard to clamp the component in place. Adjust the first screw to make sure the clamp points downhill into the component. If building your own, use high-quality fine plywood or a composite material. A half-inch piece of plywood should have 10+ layers. Baltic birch B/BB grade should work well and is more common than the material used here, which was salvaged from an instrument shipping crate. MDF and Corian have been used for similar purposes in the past.

- Cuvette 

	The cuvette is made of 1/16" glass, glued with clear silicone sealant. The 100% silicone version seems to have the best chemical resistance and makes the strongest bond with glass.  The purchased 2" x 2" plates were glued together into a 5-sided open cube.  It took a couple of rounds of testing and resealing to initially stop all of the leaks. Even so leaks still appeared with the immersion fluid in the cuvette.  This is an obvious area for improvement. 

- Arduino

	Arduino Uno is used to translate USB serial commands into pin toggles and motion. Commands to move the Canon lens and theta motor, plus control laser power are included in the associated sketch. Any similar microcontroller with an SPI port, 6+ GPIOs, and a USB serial could be substituted. 

- Software

	Webcamoid was used to capture images. It's free and exposes enough parameters to set exposure time on a cheap USB webcam. 
	Python code for a mediocre GUI is included.  It can stream and record from a webcam and communicate with the Arduino via PC.  In practice it was used for controlling the theta motor for specimen positioning.  Could be improved for more utility. 


### Preparation of cleared balsa wood

- Requirements

	Light sheet microscopy works best with an optically clear specimen.  Here the goal is to produce such a specimen for demonstrating the capability of the assembled microscope. Ideally this specimen and required reagents are readily available, inexpensive, unharmful, and amenable to a straightforward clearing protocol.  I define 'readily availble' as 'can be purchased easily on the internet' and 'unharmful' being 'ok to use in your garage without a respirator'.  Here I present a protocol for generating optically clear balsa wood using sodium chlorite and benzyl alcohol.
	
	Tissue clearing protocols for biomedical applications are presently an area of great research interest with dozens of published approaches for generating optically transparent mammalian tissue.  Typically these protocols involve two steps - a 'clearing' step in which scattering or absorbing material in the specimen is removed and an 'index matching' step where the cleared specimen is infiltrated and submerged in an fluid of matching refractive index to the specimen.  Together these steps aim to render the specimen optically transparent while in the index matching fluid. Unfortunately many of these protocols require reagents that are sticky, stinky, toxic, or otherwise incompatible with a home lab.  Imaging cleared tissue also requires harvesting or purchasing said tissue, a process I'd like to avoid.
	
	Thankfully plant tissue is reliably available in its dried and inert form at the local hardware, hobby, or art supply store in the form of balsa wood. This material shows interesting structure at the length scales observable on this instrument. Clear wood is an active area of research, with available [protocols] (https://pubs.rsc.org/en/content/articlelanding/2020/ra/d0ra07409h) usually with the aim of making optically clear biocomposites. This protocol is adapted here to use a fluid rather than embedded plastic for homogenizing the refractive index.  
	

- Protocol 

	Balsa wood sheets 3/32" (~2 mm) thick (4" wide x 36" long) were purchased from the typical display rack at a local art supply store. Pieces ~1 cm x 2 cm were cut from this stock. The pieces were cleared in a 1% sodium chlorite solution in 10% acetic acid at 80 deg C overnight. This bleached the wood from natural to white in color. Bleached pieces were dehydrated and delipidated in 40% ethanol, 99% isopropanol, and acetone for 1-24 hrs each step. These pieces were carried through attempts at index matching with glycerol (wrong index), tung oil (fluorescent), and anisole (close but sub-optimal). Benzyl alcohol produced pieces the most optically clear of any the fluids tested after a couple hours of immersion in this fluid. All pieces were immersed in benzyl alcohol to clear and imaged in this fluid. Specimens were mounted using UV-activated adhesive (EDSRDXS UV bonding glue) directly to the shaft of the theta motor. 

- Remarks

	Pieces the full thickness tested (> 2 mm) were successfully cleared using this method. Benzyl alcohol is not a perfect match for the resulting refractive index of the cleared and delipidated material, but a series of anisole:benzyl benzaldehyde or isopropanol:benzyl benzaldehyde did not produce clearer specimens at or around the refractive index of benzyl alcohol. 
	
	Superglue (cyanoacrylate) did not adhere to the specimens in benzyl alcohol.  The UV adhesive does slowly soften in benzyl alcohol.  It helps to add additional material to build up a stronger joint when mounting. 
	
	The wood pores may be challenging to clear of air bubbles at immersion steps. A vacuum pump to evacuate the immersion vessel aids in removing these bubbles. I used a manual pump intended for clearing hydraulic brake lines on a car. This did help remove bubbles from the specimen pieces though a stronger vacuum could move this process along more quickly. 
	
	
- Imaging

	Images were captured using Webcamoid software and the camera set to the highest exposure time availble. For each static image, 8 captures were combined into a single composite image using ImageJ.  Each of the 8 images was imported, combined into a stack, converted to 32-bit grayscale, and summed along the Z axis. The resulting images were cropped and constrast-adjusted for display. 
	
	The Z stack video was captured using the same software in video mode. Action along the Z axis was accomplished by manually turning an accessible drive gear in the Z axis slide.  Videos were cropped and contrast-adjusted for display. 
	
	Autofluorescence from the balsa wood provides the observable signal. This is dim. If more signal is required then staining the specimen with a fluorescent dye would be appropriate.

- Calibration

	Image size was calibrated with an of a ruler marked in millimeter increments. With the 0.5x telecentric lens this gives a pixel size of 1.07 µm/pixel; the datasheet gives 1.12 µm/pixel so these numbers agree well.  The full field of view is 4.9 mm x 3.7 mm.
	
	Resolution was measured by finding a point-like source in a captured image. A point-like feature was identified and the intensity vs distance profile across this feature was fit to a Gaussian function. This fit gives a σ = 1.43, or full width half max value of 3.37 pixels, corresponding to a resolution of 14.5 µm.   


### Results

Static images show pores (~250 µm diameter) and tool marks from the milling saw. These pores can be followed through the depth of the specimen in the Z stack video data.  One pore contains an air bubble that is visible as inclusions in the deeper planes of the stack; fully wetted pores do not show this issue.  

Thing works fine.


- Comparison to goals

1. OPT w/ telecentric lens
   
   The resulting images are sufficient quality to consider this a success.  A $50 telecentric lens from eBay can work just fine for this level of imaging. 

2. Light sheet w/ DSLR lens

   A DSLR lens and small cylindrical lens can work together to create a mesoscopic light sheet.  The axial position of this sheet moves in response to zoom and focus position of the lens for coarse and fine control, respectively. The motorized focus control can, in principle, be used to generate 'tiled' light sheet images by moving the beam waist precisely across the field of view. In practice this effect is small when using the motorized focus only. In practice this was not used and instead beam waist adjustments made with the zoom feature alone. Another application or longer working distance could make this approach more useful. Even without the motorization a DSLR lens makes a reasonable objective lens for light sheet generation at this scale.

3. Theatrical dichroics 

   A stacked pair of Industrial Green dichroics did a fine job blocking scatter from the 80 mW 450 nm laser beam. A green emission component from the laser was found in testing. This is a common issue with cheap blue diode lasers and is mitigated with an excitation filter. Thankfully the beam diameter at this point is small (<< 5 mm) so the required excitation filter is not expensive. In total all three filters, including the pair of 1.95" emission filters was under $100, shipped. For applications requiring a large dichroic and loose spectral tolerances these theatrical dichroic filters can produce excellent fluorescent images. 

4. Clearing protocol 
 
   A protcol for optically cleared balsa wood compabile with light sheet microscopy is demonstrated. The material produced is transparent and sufficient clarity to read text through a 2 mm piece. Images show residual scattering from the specimen when attempting to image through the specimen at a depth beyond ~1 mm.  This is visible in the presented video where the right side of the specimen is blurred.  This portion of the specimen is imaged through the thickness of the sample.  Photons from the left side of the specimen do not have to pass through more specimen to reach the detector and remain unblurred. More precise index matching may mitigate this effect. Static images taken at the end face of the specimen do not show this issue.  To my knowledge this is the first presentation of cleared balsa wood for optical microscopy.

5. LOLs  

   Plenty

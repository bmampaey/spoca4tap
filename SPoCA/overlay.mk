CC=g++
TRACKINGLFLAGS=-lpthread
IDLLFLAGS=-L /usr/local/idl/idl706/bin/bin.linux.x86_64 -lpthread -lidl -lXp -lXpm -lXmu -lXext -lXt -lSM -lICE  -lXinerama -lX11 -ldl -ltermcap -lrt -lm /usr/lib/libXm.a
MAGICKLFLAGS=`Magick++-config --ldflags --libs`
MAGICKCFLAGS=`Magick++-config --cppflags`
CFLAGS=-Wall -fkeep-inline-functions -g -O3 $(MAGICKCFLAGS) 
LFLAGS=-lcfitsio $(MAGICKLFLAGS) 
DFLAGS= -DMAGICK 

all:bin/overlay.x
clean: rm bin/overlay.x objects/overlay.o objects/EUVImage.o objects/SunImage.o objects/FitsFile.o objects/Header.o objects/WCS.o objects/Image.o objects/Coordinate.o objects/MagickImage.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/FeatureVector.o objects/tools.o


bin/overlay.x : overlay.mk objects/overlay.o objects/EUVImage.o objects/SunImage.o objects/FitsFile.o objects/Header.o objects/WCS.o objects/Image.o objects/Coordinate.o objects/MagickImage.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/FeatureVector.o objects/tools.o | bin
	$(CC) $(CFLAGS) $(DFLAGS) objects/overlay.o objects/EUVImage.o objects/SunImage.o objects/FitsFile.o objects/Header.o objects/WCS.o objects/Image.o objects/Coordinate.o objects/MagickImage.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/FeatureVector.o objects/tools.o $(LFLAGS) -o bin/overlay.x

objects/overlay.o : overlay.mk programs/overlay.cpp classes/tools.h classes/constants.h classes/mainutilities.h classes/ArgParser.h classes/ColorMap.h classes/MagickImage.h classes/EUVImage.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) programs/overlay.cpp -o objects/overlay.o

objects/EUVImage.o : overlay.mk classes/EUVImage.cpp classes/Coordinate.h classes/SunImage.h classes/MagickImage.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EUVImage.cpp -o objects/EUVImage.o

objects/SunImage.o : overlay.mk classes/SunImage.cpp classes/Image.h classes/WCS.h classes/Header.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SunImage.cpp -o objects/SunImage.o

objects/FitsFile.o : overlay.mk classes/FitsFile.cpp classes/tools.h classes/constants.h classes/Header.h classes/Coordinate.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FitsFile.cpp -o objects/FitsFile.o

objects/Header.o : overlay.mk classes/Header.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Header.cpp -o objects/Header.o

objects/WCS.o : overlay.mk classes/WCS.cpp classes/constants.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/WCS.cpp -o objects/WCS.o

objects/Image.o : overlay.mk classes/Image.cpp classes/tools.h classes/constants.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Image.cpp -o objects/Image.o

objects/Coordinate.o : overlay.mk classes/Coordinate.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Coordinate.cpp -o objects/Coordinate.o

objects/MagickImage.o : overlay.mk classes/MagickImage.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/MagickImage.cpp -o objects/MagickImage.o

objects/ColorMap.o : overlay.mk classes/ColorMap.cpp classes/Header.h classes/SunImage.h classes/gradient.h classes/MagickImage.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/ColorMap.cpp -o objects/ColorMap.o

objects/ArgParser.o : overlay.mk classes/ArgParser.cpp | objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/ArgParser.cpp -o objects/ArgParser.o

objects/mainutilities.o : overlay.mk classes/mainutilities.cpp classes/FeatureVector.h classes/EUVImage.h classes/EITImage.h classes/EUVIImage.h classes/AIAImage.h classes/SWAPImage.h classes/HMIImage.h classes/SUVIImage.h classes/ColorMap.h classes/Header.h classes/Coordinate.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/mainutilities.cpp -o objects/mainutilities.o

objects/SUVIImage.o : overlay.mk classes/SUVIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SUVIImage.cpp -o objects/SUVIImage.o

objects/HMIImage.o : overlay.mk classes/HMIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/HMIImage.cpp -o objects/HMIImage.o

objects/SWAPImage.o : overlay.mk classes/SWAPImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SWAPImage.cpp -o objects/SWAPImage.o

objects/AIAImage.o : overlay.mk classes/AIAImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/AIAImage.cpp -o objects/AIAImage.o

objects/EUVIImage.o : overlay.mk classes/EUVIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EUVIImage.cpp -o objects/EUVIImage.o

objects/EITImage.o : overlay.mk classes/EITImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EITImage.cpp -o objects/EITImage.o

objects/FeatureVector.o : overlay.mk classes/FeatureVector.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FeatureVector.cpp -o objects/FeatureVector.o

objects/tools.o : overlay.mk classes/tools.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/tools.cpp -o objects/tools.o

objects : 
	 mkdir -p objects

bin : 
	 mkdir -p bin

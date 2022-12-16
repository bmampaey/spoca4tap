CC=g++
TRACKINGLFLAGS=-lpthread
IDLLFLAGS=-L /usr/local/idl/idl706/bin/bin.linux.x86_64 -lpthread -lidl -lXp -lXpm -lXmu -lXext -lXt -lSM -lICE  -lXinerama -lX11 -ldl -ltermcap -lrt -lm /usr/lib/libXm.a
MAGICKLFLAGS=`Magick++-config --ldflags --libs`
MAGICKCFLAGS=`Magick++-config --cppflags`
CFLAGS=-Wall -fkeep-inline-functions -g -O3
LFLAGS=-lcfitsio
DFLAGS=

all:bin/get_ch_map.x
clean: rm bin/get_ch_map.x objects/get_ch_map.o objects/CoronalHole.o objects/FitsFile.o objects/Coordinate.o objects/Header.o objects/RegionStats.o objects/SegmentationStats.o objects/Region.o objects/EUVImage.o objects/SunImage.o objects/WCS.o objects/Image.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/FeatureVector.o objects/tools.o


bin/get_ch_map.x : get_ch_map.mk objects/get_ch_map.o objects/CoronalHole.o objects/FitsFile.o objects/Coordinate.o objects/Header.o objects/RegionStats.o objects/SegmentationStats.o objects/Region.o objects/EUVImage.o objects/SunImage.o objects/WCS.o objects/Image.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/FeatureVector.o objects/tools.o | bin
	$(CC) $(CFLAGS) $(DFLAGS) objects/get_ch_map.o objects/CoronalHole.o objects/FitsFile.o objects/Coordinate.o objects/Header.o objects/RegionStats.o objects/SegmentationStats.o objects/Region.o objects/EUVImage.o objects/SunImage.o objects/WCS.o objects/Image.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/FeatureVector.o objects/tools.o $(LFLAGS) -o bin/get_ch_map.x

objects/get_ch_map.o : get_ch_map.mk programs/get_CH_map.cpp classes/tools.h classes/constants.h classes/mainutilities.h classes/ArgParser.h classes/ColorMap.h classes/EUVImage.h classes/CoronalHole.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) programs/get_CH_map.cpp -o objects/get_ch_map.o

objects/CoronalHole.o : get_ch_map.mk classes/CoronalHole.cpp classes/EUVImage.h classes/ColorMap.h classes/Region.h classes/RegionStats.h classes/FitsFile.h classes/ArgParser.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/CoronalHole.cpp -o objects/CoronalHole.o

objects/FitsFile.o : get_ch_map.mk classes/FitsFile.cpp classes/tools.h classes/constants.h classes/Header.h classes/Coordinate.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FitsFile.cpp -o objects/FitsFile.o

objects/Coordinate.o : get_ch_map.mk classes/Coordinate.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Coordinate.cpp -o objects/Coordinate.o

objects/Header.o : get_ch_map.mk classes/Header.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Header.cpp -o objects/Header.o

objects/RegionStats.o : get_ch_map.mk classes/RegionStats.cpp classes/constants.h classes/tools.h classes/Coordinate.h classes/EUVImage.h classes/ColorMap.h classes/FitsFile.h classes/Region.h classes/SegmentationStats.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/RegionStats.cpp -o objects/RegionStats.o

objects/SegmentationStats.o : get_ch_map.mk classes/SegmentationStats.cpp classes/constants.h classes/tools.h classes/Coordinate.h classes/EUVImage.h classes/ColorMap.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SegmentationStats.cpp -o objects/SegmentationStats.o

objects/Region.o : get_ch_map.mk classes/Region.cpp classes/constants.h classes/tools.h classes/Coordinate.h classes/ColorMap.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Region.cpp -o objects/Region.o

objects/EUVImage.o : get_ch_map.mk classes/EUVImage.cpp classes/Coordinate.h classes/SunImage.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EUVImage.cpp -o objects/EUVImage.o

objects/SunImage.o : get_ch_map.mk classes/SunImage.cpp classes/Image.h classes/WCS.h classes/Header.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SunImage.cpp -o objects/SunImage.o

objects/WCS.o : get_ch_map.mk classes/WCS.cpp classes/constants.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/WCS.cpp -o objects/WCS.o

objects/Image.o : get_ch_map.mk classes/Image.cpp classes/tools.h classes/constants.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Image.cpp -o objects/Image.o

objects/ColorMap.o : get_ch_map.mk classes/ColorMap.cpp classes/Header.h classes/SunImage.h classes/gradient.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/ColorMap.cpp -o objects/ColorMap.o

objects/ArgParser.o : get_ch_map.mk classes/ArgParser.cpp | objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/ArgParser.cpp -o objects/ArgParser.o

objects/mainutilities.o : get_ch_map.mk classes/mainutilities.cpp classes/FeatureVector.h classes/EUVImage.h classes/EITImage.h classes/EUVIImage.h classes/AIAImage.h classes/SWAPImage.h classes/HMIImage.h classes/SUVIImage.h classes/ColorMap.h classes/Header.h classes/Coordinate.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/mainutilities.cpp -o objects/mainutilities.o

objects/SUVIImage.o : get_ch_map.mk classes/SUVIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SUVIImage.cpp -o objects/SUVIImage.o

objects/HMIImage.o : get_ch_map.mk classes/HMIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/HMIImage.cpp -o objects/HMIImage.o

objects/SWAPImage.o : get_ch_map.mk classes/SWAPImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SWAPImage.cpp -o objects/SWAPImage.o

objects/AIAImage.o : get_ch_map.mk classes/AIAImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/AIAImage.cpp -o objects/AIAImage.o

objects/EUVIImage.o : get_ch_map.mk classes/EUVIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EUVIImage.cpp -o objects/EUVIImage.o

objects/EITImage.o : get_ch_map.mk classes/EITImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EITImage.cpp -o objects/EITImage.o

objects/FeatureVector.o : get_ch_map.mk classes/FeatureVector.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FeatureVector.cpp -o objects/FeatureVector.o

objects/tools.o : get_ch_map.mk classes/tools.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/tools.cpp -o objects/tools.o

objects :
	 mkdir -p objects

bin :
	 mkdir -p bin

CC=g++
TRACKINGLFLAGS=-lpthread
IDLLFLAGS=-L /usr/local/idl/idl706/bin/bin.linux.x86_64 -lpthread -lidl -lXp -lXpm -lXmu -lXext -lXt -lSM -lICE  -lXinerama -lX11 -ldl -ltermcap -lrt -lm /usr/lib/libXm.a
MAGICKLFLAGS=`Magick++-config --ldflags --libs`
MAGICKCFLAGS=`Magick++-config --cppflags`
CFLAGS=-Wall -fkeep-inline-functions -g -O3
LFLAGS=-lcfitsio
DFLAGS=-DNUMBERCHANNELS=1

all:bin/ch_attribution.x
clean: rm bin/ch_attribution.x objects/ch_attribution.o objects/FitsFile.o objects/Coordinate.o objects/Header.o objects/SegmentationStats.o objects/FeatureVector.o objects/SPoCA2Classifier.o objects/SPoCAClassifier.o objects/PCM2Classifier.o objects/PFCMClassifier.o objects/PCMClassifier.o objects/FCMClassifier.o objects/Image.o objects/Classifier.o objects/Region.o objects/EUVImage.o objects/SunImage.o objects/WCS.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/tools.o


bin/ch_attribution.x : ch_attribution.mk objects/ch_attribution.o objects/FitsFile.o objects/Coordinate.o objects/Header.o objects/SegmentationStats.o objects/FeatureVector.o objects/SPoCA2Classifier.o objects/SPoCAClassifier.o objects/PCM2Classifier.o objects/PFCMClassifier.o objects/PCMClassifier.o objects/FCMClassifier.o objects/Image.o objects/Classifier.o objects/Region.o objects/EUVImage.o objects/SunImage.o objects/WCS.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/tools.o | bin
	$(CC) $(CFLAGS) $(DFLAGS) objects/ch_attribution.o objects/FitsFile.o objects/Coordinate.o objects/Header.o objects/SegmentationStats.o objects/FeatureVector.o objects/SPoCA2Classifier.o objects/SPoCAClassifier.o objects/PCM2Classifier.o objects/PFCMClassifier.o objects/PCMClassifier.o objects/FCMClassifier.o objects/Image.o objects/Classifier.o objects/Region.o objects/EUVImage.o objects/SunImage.o objects/WCS.o objects/ColorMap.o objects/ArgParser.o objects/mainutilities.o objects/SUVIImage.o objects/HMIImage.o objects/SWAPImage.o objects/AIAImage.o objects/EUVIImage.o objects/EITImage.o objects/tools.o $(LFLAGS) -o bin/ch_attribution.x

objects/ch_attribution.o : ch_attribution.mk programs/attribution.cpp classes/tools.h classes/constants.h classes/mainutilities.h classes/ArgParser.h classes/ColorMap.h classes/EUVImage.h classes/Classifier.h classes/FCMClassifier.h classes/PCMClassifier.h classes/PFCMClassifier.h classes/PCM2Classifier.h classes/SPoCAClassifier.h classes/SPoCA2Classifier.h classes/FeatureVector.h classes/SegmentationStats.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) programs/attribution.cpp -o objects/ch_attribution.o

objects/FitsFile.o : ch_attribution.mk classes/FitsFile.cpp classes/tools.h classes/constants.h classes/Header.h classes/Coordinate.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FitsFile.cpp -o objects/FitsFile.o

objects/Coordinate.o : ch_attribution.mk classes/Coordinate.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Coordinate.cpp -o objects/Coordinate.o

objects/Header.o : ch_attribution.mk classes/Header.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Header.cpp -o objects/Header.o

objects/SegmentationStats.o : ch_attribution.mk classes/SegmentationStats.cpp classes/constants.h classes/tools.h classes/Coordinate.h classes/EUVImage.h classes/ColorMap.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SegmentationStats.cpp -o objects/SegmentationStats.o

objects/FeatureVector.o : ch_attribution.mk classes/FeatureVector.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FeatureVector.cpp -o objects/FeatureVector.o

objects/SPoCA2Classifier.o : ch_attribution.mk classes/SPoCA2Classifier.cpp classes/EUVImage.h classes/FeatureVector.h classes/PCM2Classifier.h classes/SPoCAClassifier.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SPoCA2Classifier.cpp -o objects/SPoCA2Classifier.o

objects/SPoCAClassifier.o : ch_attribution.mk classes/SPoCAClassifier.cpp classes/EUVImage.h classes/FeatureVector.h classes/PCMClassifier.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SPoCAClassifier.cpp -o objects/SPoCAClassifier.o

objects/PCM2Classifier.o : ch_attribution.mk classes/PCM2Classifier.cpp classes/EUVImage.h classes/FeatureVector.h classes/PCMClassifier.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/PCM2Classifier.cpp -o objects/PCM2Classifier.o

objects/PFCMClassifier.o : ch_attribution.mk classes/PFCMClassifier.cpp classes/EUVImage.h classes/FeatureVector.h classes/PCMClassifier.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/PFCMClassifier.cpp -o objects/PFCMClassifier.o

objects/PCMClassifier.o : ch_attribution.mk classes/PCMClassifier.cpp classes/EUVImage.h classes/FeatureVector.h classes/FCMClassifier.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/PCMClassifier.cpp -o objects/PCMClassifier.o

objects/FCMClassifier.o : ch_attribution.mk classes/FCMClassifier.cpp classes/Image.h classes/EUVImage.h classes/FeatureVector.h classes/Classifier.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/FCMClassifier.cpp -o objects/FCMClassifier.o

objects/Image.o : ch_attribution.mk classes/Image.cpp classes/tools.h classes/constants.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Image.cpp -o objects/Image.o

objects/Classifier.o : ch_attribution.mk classes/Classifier.cpp classes/tools.h classes/constants.h classes/Image.h classes/EUVImage.h classes/ColorMap.h classes/FeatureVector.h classes/Region.h classes/Coordinate.h classes/ArgParser.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Classifier.cpp -o objects/Classifier.o

objects/Region.o : ch_attribution.mk classes/Region.cpp classes/constants.h classes/tools.h classes/Coordinate.h classes/ColorMap.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/Region.cpp -o objects/Region.o

objects/EUVImage.o : ch_attribution.mk classes/EUVImage.cpp classes/Coordinate.h classes/SunImage.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EUVImage.cpp -o objects/EUVImage.o

objects/SunImage.o : ch_attribution.mk classes/SunImage.cpp classes/Image.h classes/WCS.h classes/Header.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SunImage.cpp -o objects/SunImage.o

objects/WCS.o : ch_attribution.mk classes/WCS.cpp classes/constants.h classes/Coordinate.h classes/FitsFile.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/WCS.cpp -o objects/WCS.o

objects/ColorMap.o : ch_attribution.mk classes/ColorMap.cpp classes/Header.h classes/SunImage.h classes/gradient.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/ColorMap.cpp -o objects/ColorMap.o

objects/ArgParser.o : ch_attribution.mk classes/ArgParser.cpp | objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/ArgParser.cpp -o objects/ArgParser.o

objects/mainutilities.o : ch_attribution.mk classes/mainutilities.cpp classes/FeatureVector.h classes/EUVImage.h classes/EITImage.h classes/EUVIImage.h classes/AIAImage.h classes/SWAPImage.h classes/HMIImage.h classes/SUVIImage.h classes/ColorMap.h classes/Header.h classes/Coordinate.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/mainutilities.cpp -o objects/mainutilities.o

objects/SUVIImage.o : ch_attribution.mk classes/SUVIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SUVIImage.cpp -o objects/SUVIImage.o

objects/HMIImage.o : ch_attribution.mk classes/HMIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/HMIImage.cpp -o objects/HMIImage.o

objects/SWAPImage.o : ch_attribution.mk classes/SWAPImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/SWAPImage.cpp -o objects/SWAPImage.o

objects/AIAImage.o : ch_attribution.mk classes/AIAImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/AIAImage.cpp -o objects/AIAImage.o

objects/EUVIImage.o : ch_attribution.mk classes/EUVIImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EUVIImage.cpp -o objects/EUVIImage.o

objects/EITImage.o : ch_attribution.mk classes/EITImage.cpp classes/EUVImage.h classes/Header.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/EITImage.cpp -o objects/EITImage.o

objects/tools.o : ch_attribution.mk classes/tools.cpp classes/constants.h| objects
	$(CC) -c $(CFLAGS) $(DFLAGS) classes/tools.cpp -o objects/tools.o

objects :
	 mkdir -p objects

bin :
	 mkdir -p bin

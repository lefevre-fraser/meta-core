"""

Adams2AbaqusParse.py, version 1.1.0

For use with Abaqus 6.13-1 (Python 2.6.2).

Created by Ozgur Yapar <oyapar@isis.vanderbilt.edu>

    - Includes modules which parse the XML files generated by CyPhy
      and Create Assembly program to get the essential data which
      contains user inputs and CAD data.

"""

from abaqus import *
from abaqusConstants import *
import os, re
from numpy import array, cross, transpose, vstack, dot
import numpy.linalg as LA
import string as STR
import xml.etree.ElementTree as ET
import _winreg, sys, ctypes, uuid, traceback


MAIN = os.getcwd()                                                           # initial working directory
LOGDIR = os.path.join(MAIN, "log", "CyPhy2AbaqusCmd.log")                    # path to log file
	
# returns the material library data
def parseMaterialLibrary():
    with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'Software\META', 0, _winreg.KEY_READ) as key:
        META_PATH = _winreg.QueryValueEx(key, 'META_PATH')[0]

    MATERIALLIBINTERFACEPATH = os.path.join(META_PATH, "bin", "Python27", "Lib", "site-packages")

    sys.path.insert(0, MATERIALLIBINTERFACEPATH)
    import sitecustomize
    from MaterialLibraryInterface import LibraryManager

    PATH = ctypes.c_wchar_p(chr(0x00) * 256)
    FOLDERID_DOCUMENTS = ctypes.c_char_p(uuid.UUID("ED4824AF-DCE4-45A8-81E2-FC7965083634").bytes_le)
    ctypes.windll.shell32.SHGetKnownFolderPath(FOLDERID_DOCUMENTS, 0, None, ctypes.byref(PATH))
    MATERIALLIBPATH = os.path.join(PATH.value, "META Documents", "MaterialLibrary", "material_library.json")

    LIBRARY_MANAGER = LibraryManager(MATERIALLIBPATH)

    return LIBRARY_MANAGER

def parseCADAssemblyXML():
    f_p = open(LOGDIR, "w")

    try:
        f_p.write("XML parser is obtaining necessary data from CyPhy" + '\n')                     #XML parser obtains necessary data from CyPhy
        
        xmlName = 'CADAssembly.xml'
        xmlPath = os.path.join(MAIN, xmlName)

        f_p.write("Reading data from CADAssembly.xml" + '\n')
        
        try:
            tree = ET.parse(xmlPath)
            xmlRoot = tree.getroot()
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot parse CADAssembly.xml.\n')
            raise
        
        try:
            assemblyXML = xmlRoot.find('Assembly')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Assembly/" in CADAssembly.xml.\n')
            raise
            
        try:
            analysesXML = assemblyXML.find('Analyses')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Analyses/" in CADAssembly.xml.\n')
            raise

        try:
            cadAssemblyXML = assemblyXML.find('CADComponent')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"CADComponent/" in CADAssembly.xml.\n')
            raise
            
        try:
            feaXML = analysesXML.find('FEA')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"FEA/" in CADAssembly.xml.\n')
            raise

        try:
            metricSetXML = feaXML.getiterator('Metric')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find \"Metric\" inside the block FEA in CADAssembly.xml.\n')
            raise
        
        
        try:
            metricsSetXML = feaXML.find('Metrics')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find \"Metrics\" inside the block \"FEA\" in CADAssembly.xml.\n')
            raise
        
        try:
            metricsComponentSetXML = metricsSetXML.findall('Metric')
        except:
            metricsComponentSetXML = 'null'
            pass

        try:
            maxNumberIter = int(feaXML.get("MaxAdaptiveIterations"))
            if maxNumberIter > 10:
                maxNumberIter = 10
            elif maxNumberIter <= 0:
                maxNumberIter = 1
        except Exception as e:
            f.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f.write('ERROR: Error in reading maximum number of iterations from CADAssembly.xml file.\n')
            raise

    except Exception as e:
        f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
        f_p.write('ERROR: Error in reading CADAssembly.xml file.\n')
        raise

    f_p.close()

    return (xmlName, feaXML, cadAssemblyXML, metricSetXML, metricsComponentSetXML, maxNumberIter)

def parseCADAssemblyMetricsXML():
    f_p = open(LOGDIR, "w")

    try:
        f_p.write("XML parser is obtaining necessary data from Create Assemby program" + '\n')
        
        xmlMetricsName = 'CADAssembly_metrics.xml'
        xmlMetricsPath = os.path.join(MAIN, xmlMetricsName)

        f_p.write("Reading data from CADAssembly_metrics.xml" + '\n')
        
        try:
            treeMetrics = ET.parse(xmlMetricsPath)
            xmlMetricsRoot = treeMetrics.getroot()
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot parse CADAssembly_metrics.xml.\n')
            raise

        try:    
            metricComponentsXML = xmlMetricsRoot.find('MetricComponents')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"MetricComponents/" in CADAssembly_metrics.xml.\n')
            raise

        try:    
            jointsMBDXML = xmlMetricsRoot.find('Joints')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Joints/" in CADAssembly_metrics.xml.\n')
            raise
            
    except Exception as e:
        f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
        f_p.write('ERROR: Error in reading CADAssembly_metrics.xml file.\n')
        raise

    f_p.close()

    return (xmlMetricsName, metricComponentsXML, jointsMBDXML)

def parseStep(cadAssemblyXML):
    f_p = open(LOGDIR, "w")

    # define the path to the STEP file and open it
    f_p.write("Defining the path for the STEP file" + '\n')
    try:
        if cadAssemblyXML.get("Type") == "ASSEMBLY":
            testBenchName = cadAssemblyXML.get("Name")
        stepName = testBenchName + '_asm.stp'
        stepPath = os.path.join(MAIN, 'AP203_E2_SINGLE_FILE', stepName)
        step = mdb.openStep(fileName=stepPath)
    except Exception as e:
        f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
        f_p.write('ERROR: Error during finding and opening the step file\n')
        raise

    f_p.write("Opening the STEP file " + str(stepName) + ' and converting it into raw data' + '\n')

    f_p.write('\n')
    f_p.write("**********************************************************************************" + '\n')
    f_p.write('\n')

    f_p.close()

    return (stepPath, testBenchName, step)

def parseKinComputedValuesXML():
    f_p = open(LOGDIR, "w")
    
    try:
        f_p.write("XML parser is obtaining necessary data from Adams" + '\n')                     #XML parser obtains necessary data from CyPhy
        
        xmlCompName = 'kinComputedValues.xml'
        xmlCompPath = os.path.join(MAIN, xmlCompName)

        f_p.write("Reading data from ComputedValues.xml" + '\n')
        
        try:
            treeComp = ET.parse(xmlCompPath)
            xmlCompRoot = treeComp.getroot()
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot parse ComputedValues.xml.\n')
            raise

        try:
            ComputedComponentXML = xmlCompRoot.findall('Component')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find \"Components\" block inside the ComputedValues.xml file.\n')
            raise

        try:
            for element in ComputedComponentXML:
                compMetrics = element.find('Metrics')
                compMetric = compMetrics.find('Metric')
                try:
                    compMetricID = compMetric.get('MetricID')
                    if compMetricID == 'Anchor':
                        anchorID = element.get('ComponentInstanceID')
                        anchorPoint = compMetric.get('ArrayValue')
                except:
                    pass
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find anchored part name inside the ComputedValues.xml file.\n')
            raise

    except Exception as e:
        f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
        f_p.write('ERROR: Error in reading ComputedValues.xml file.\n')
        raise

    f_p.close()

    return (anchorID, anchorPoint)

def parseCADAssemblyReqDataXML():
    f_p = open(LOGDIR, "w")
    
    try:
        f_p.write("XML parser is obtaining necessary data from Adams" + '\n')                     #XML parser obtains necessary data from CyPhy
        
        xmlReqName = 'CADAssembly_requestedData.xml'
        xmlReqPath = os.path.join(MAIN, xmlReqName)

        f_p.write("Reading data from CADAssembly_requestedData.xml" + '\n')
        
        try:
            treeReq = ET.parse(xmlReqPath)
            xmlReqRoot = treeReq.getroot()
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot parse CADAssembly_requestedData.xml.\n')
            raise

    except Exception as e:
        f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
        f_p.write('ERROR: Error in reading CADAssembly_requestedData.xml file.\n')
        raise

    f_p.close()

    return (xmlReqRoot)

def parseSampleAMBDXML():
    f_p = open(LOGDIR, "w")

    try:
        f_p.write("XML parser is obtaining necessary data from Adams" + '\n')                     #XML parser obtains necessary data from CyPhy
        
        xmlMBDName = 'Sample2_AMBD.xml'
        xmlMBDPath = os.path.join(MAIN, xmlMBDName)

        f_p.write("Reading data from Sample2_AMBD.xml" + '\n')
        
        try:
            treeMBD = ET.parse(xmlMBDPath)
            xmlMBDRoot = treeMBD.getroot()
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot parse Sample2_AMBD.xml.\n')
            raise

        try:
            assemblyMBDXML = xmlMBDRoot.find('Assembly')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Assembly/" in Sample2_AMBD.xml.\n')
            raise

        try:
            jointsMBDXML = assemblyMBDXML.find('Joints')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Joints/" in Sample2_AMBD.xml.\n')
            raise

        try:
            componentsMBDXML = assemblyMBDXML.find('Components')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Components/" in Sample2_AMBD.xml.\n')
            raise

        try:
            anchorMBDXML = componentsMBDXML.find('Anchor')
            anchorID = anchorMBDXML.get('ID')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the block /"Anchor/" in Sample2_AMBD.xml.\n')
            raise

        try:
            anchorGeometryMBDXML = anchorMBDXML.find('Geometry')
            anchorPointID = anchorGeometryMBDXML.get('MetricID')
        except:
            f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
            f_p.write('ERROR: Cannot find the MetricID for /"Anchor/" in Sample2_AMBD.xml.\n')
            raise

    except Exception as e:
        f_p.write(STR.join(traceback.format_exception(*sys.exc_info())))
        f_p.write('ERROR: Error in reading Sample2_AMBD.xml file.\n')
        raise

    f_p.close()

    return (jointsMBDXML,componentsMBDXML, anchorID, anchorPointID)

def parseInpTemp(inpTempFile):                                                                              # Determine upto which point the temporary INP file needs to be merged...
                                                                                                            # ...with the final INP file
    f_p = open(LOGDIR, "w")

    m=1
    for eachLine in inpTempFile:                                                                            # Loop through each line of the temporary INP file
        loadData = eachLine.split()                                                                         # Split each line to thier words
        try:
            if loadData[1] == 'STEP:':                                                                      # If the second word in that line is STEP:
                stopLine = m-1                                                                              # Store the number of the previous line as the stopLine
        except:
            pass
        m+=1

    f_p.close()

    return (stopLine)


def parseLOD(lodFile):                                                                                  # Determine from which point the LOD file generated by Adams needs...
                                                                                                            # ...to be merged with the final INP file
    f_p = open(LOGDIR, "w")

    j=1
    for eachLine in lodFile:                                                                                # Loop through each line of the LOD file
        loadData = eachLine.split()                                                                         # Split each line to thier words
        try:
            if loadData[2] == 'CASE':                                                                       # If the third word in that line is CASE
                startLine = j                                                                               # Store the number of that line as the startLine
                break
        except:
            pass
        j+=1

    f_p.close()

    return (startLine)

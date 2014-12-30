import arcpy,sys, traceback, os, json, zmq, random, string, json
from time import localtime, strftime


def id_generator(size=6, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


try:
   
    address = "tcp://*:5559"


    #Check out ESRI Network Analyst Extension
    arcpy.CheckOutExtension("Network")
   
    Streets_ND = r"C:\Temp\ZeroMQ2\data\data.gdb\Transportation\Streets_ND"
   

    #Make OD Cost Matrix Layer
    #Uncomment below to use Meters instead of TravelTime
    #arcpy.MakeODCostMatrixLayer_na(Streets_ND, "OD Cost Matrix 2", "Meters", "", "", "", "ALLOW_UTURNS", "Oneway;RestrictedTurns", "USE_HIERARCHY", "", "STRAIGHT_LINES")
    #print "MakeODCostMatrixLayer_na"
    
   

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(address)
    


    while True:
        print "Ready to Calculate"
        fcname = id_generator()
        CostMatrixName = id_generator()
        #print fcname
      
        arcpy.MakeODCostMatrixLayer_na(Streets_ND, CostMatrixName, "TravelTime", "", "", "Meters", "ALLOW_UTURNS", "Oneway;RestrictedTurns", "USE_HIERARCHY", "", "")
    
        stops = arcpy.CreateFeatureclass_management("in_memory", fcname, "POINT")
        arcpy.AddField_management(stops, "Name", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        cur = arcpy.InsertCursor(stops)
    
        #Parse JSON Coordinates
        jdata = socket.recv_json()
        print "Start: " + strftime("%m/%d/%y %H:%M:%S",localtime())
        #jdata = socket.recv()
        #if(jdata == "stop"):
         #   keepgoing = False

        #print(jdata)
        #ignore below unless in a different projection than WGS84 (ie Lat/Long)
        #prjFile = os.path.join(arcpy.GetInstallInfo()["InstallDir"],"Coordinate Systems/Geographic Coordinate Systems/World/WGS 1984.prj")
        #spatialRef = arcpy.SpatialReference(prjFile)

        #make new point geometries from the coordinates and add them to the in-memory featureclass
        for d in jdata["Locations"]:
            pnt = arcpy.Point(d["Lon"], d["Lat"])
            pointGeometry = arcpy.PointGeometry(pnt)
            feat = cur.newRow()
            feat.shape = pointGeometry
            feat.Name = d["ID"]
            cur.insertRow(feat)
  

        fcCount = (arcpy.GetCount_management(stops))
        #print "Stops: " + fcCount.getOutput(0)

        arcpy.AddLocations_na(CostMatrixName, "Origins", stops, "Name Name #;TargetDestinationCount # #;CurbApproach # 0;Cutoff_Minutes # #;Cutoff_Meters # #;Cutoff_WeekdayFallbackTravelTime # #;Cutoff_WeekendFallbackTravelTime # #;Cutoff_TravelTime # #", "5000 Meters", "NAME", "Streets SHAPE;Streets_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE", "Streets #;Streets_ND_Junctions #")

        #print "Add Destinations". To get all connections between points, make origins and destinations the same featureclass. (ie. "stops")
        arcpy.AddLocations_na(CostMatrixName, "Destinations", stops, "Name Name #;CurbApproach # 0", "5000 Meters", "NAME", "Streets SHAPE;Streets_ND_Junctions NONE", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE", "Streets #;Streets_ND_Junctions #")

        #Solve to get results
        arcpy.Solve_na(CostMatrixName, "SKIP", "TERMINATE")

        #Gets a count of the total connections made.
        #print ("Connection Count: " + arcpy.GetCount_management("Lines").getOutput(0))
        #print ("Origsn: " + arcpy.GetCount_management("Origins").getOutput(0))
        fcSearch = arcpy.SearchCursor("Lines", "", "", "OriginID,DestinationID,Name,Total_TravelTime,Total_Meters")

        #fieldList = arcpy.ListFields("Lines")
        #for field in fieldList:
        #    print("{0} is a type of {1} with a length of {2}"
        #    .format(field.name, field.type, field.length)) 
        
        strOutput = ""
        data = []
        for fcRow in fcSearch:
            #strOutput += "From: " + str(fcRow.getValue("OriginID")) + "To: " + str(fcRow.getValue("DestinationID")) +  ", TravelTime: " + str(fcRow.getValue("Total_TravelTime")) + ", Meters: " + str(fcRow.getValue("Total_Meters")) + "\n"
            data += [ { 'From':str(fcRow.getValue("OriginID")),'To':str(fcRow.getValue("DestinationID")), 'TravelDuration':str(fcRow.getValue("Total_TravelTime")), 'Miles':str(fcRow.getValue("Total_Meters")) } ]
        
        #print strOutput
        arcpy.Delete_management(CostMatrixName)
        del  fcSearch,fcRow,cur,stops

        data_string = json.dumps(data)
        socket.send(data_string);
        print "End: " + strftime("%m/%d/%y %H:%M:%S",localtime())
        





except:
  
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\n  Traceback Info:\n" + tbinfo + "\nError Info:\n    " + \
            str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
    msgs = "arcpy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
    msgTxt="The script failed: " + "\n" + msgs + "\n" + pymsg
    print msgTxt




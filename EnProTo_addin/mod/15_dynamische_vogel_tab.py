class DynBirdTab(object):
    """Implementation for DynBirdTab.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        import arcpy
        import pythonaddins
        import logging

        #usage logging
        log_use(str(self.__class__.__name__)

        #init vars
        #positioncounter
        #iPosition = [10.0, 25.0]
        #distances of and between elements
        txtElemWidth = 6.0
        #font characteristics
        fontName = "Arial"
        headingFontSize = 14.0
        itemFontSize = 12.0

        #Get/set information about the table
        rowHeight = 0.4
        fieldNames = ["Abk", "Name_dt", "Name_wiss"]
        colWidth = 4.0
        smallColWidth = 1.5


        #Add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate",
                        tag = "txtElemTemplate", txtsize = itemFontSize)
        #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        tableText = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()

        #start coords for elements
        pageWidth = mxd.pageSize.width
        upperX = pageWidth + 3.0
        upperY = 25.0

        #get data from attribute table and store rows as tuples in list
        tabledata = []
        with arcpy.da.SearchCursor(toclayer, fieldNames) as cursor:
            for row in cursor:
                rowtuple = tuple(row)
                if rowtuple not in tabledata:
                    tabledata.append(rowtuple)

        #sort list with data
        #data = sorted(set(data), key=lambda tup: tup[1])
        #or inplace
        tabledata.sort(key=lambda tup: tup[1])

        #Place starting text element
        tableText.elementPositionX = upperX + 0.05 #slight offset
        tableText.elementPositionY = upperY

        #Create text elements based on values from the table
        y = upperY - rowHeight
        for row in tabledata:
            x = upperX + 0.05 #slight offset
            try:
                y = y - rowHeight
                for field in row:
                    newCellTxt = tableText.clone("_clone")
                    #make last field with latin name italic
                    if row.index(field) == 2:
                        field = "<ITA>" + field + "</ITA>"
                    newCellTxt.text = field
                    newCellTxt.elementPositionX = x
                    newCellTxt.elementPositionY = y
                    #make first column width smaller
                    if row.index(field) == 0:
                        curColWidth = smallColWidth
                    else:
                        curColWidth = colWidth
                    x = x + curColWidth
            except:
                print("Invalid value assignment")

        for elm in arcpy.mapping.ListLayoutElements(mxd, wildcard="txtElemTemplate"):
            elm.delete()

        pass


class DynVogelTab(object):
    """Implementation for DynVogelTab.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    @property
    def onClick(self):
        import arcpy
        import pythonaddins
        #init vars
        #positioncounter
        iPosition = [10.0, 25.0]
        #distances of and between elements
        sigwidth = 1.0
        txtElemWidth = 6.0
        sigheight = 0.5
        sig2group = 0.5
        group2item = 0.6
        item2item = 0.1
        group2group = 0.8
        #font characteristics
        fontName = "Arial"
        headingFontSize = 14.0
        itemFontSize = 12.0

        #Get/set information about the table
        rowHeight = 0.2
        fieldNames = ["Abk", "Name_dt", "Name_wiss"]
        colWidth = 1.5

        #start coords for elements
        upperX = 1.0
        upperY = 5.0


        #Add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate", tag = "txtElemTemplate",
                       txtsize = itemFontSize)
        #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        tableText = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()

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

        #width counter
        accumWidth = colWidth

        #Place starting text element
        tableText.elementPositionX = upperX + 0.05 #slight offset
        tableText.elementPositionY = upperY

        #Create text elements based on values from the table
        y = upperY - rowHeight
        for row in tabledata:
          x = upperX + 0.05 #slight offset
          try:
            for field in row:
              newCellTxt = tableText.clone("_clone")
              newCellTxt.text = field
              newCellTxt.elementPositionX = x
              newCellTxt.elementPositionY = y
              accumWidth = accumWidth + colWidth
              x = x + colWidth
            y = y - rowHeight
          except:
            print("Invalid value assignment")

        #for elm in lyt.listElements(wildcard="_clone"):
         # elm.delete()

        pass
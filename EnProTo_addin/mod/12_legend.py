class TB(object):
    """Implementation for TB.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    @property
    def onClick(self):
        import logging

        #usage logging
        user = os.environ.get("USERNAME")
        logger.info('%s, %s', "Legend", user)


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

        #helper functions
        #function to create signature with heading
        def createHeader(position, sigcolor, transparency, txtstring, txtElem):
            AddRectangleElement(position = position, bgcolor = sigcolor, bgtransparency = transparency, tag = "sig")
            heading = txtElem.clone("_clone")
            heading.elementPositionX = position[0] + sigwidth + sig2group
            heading.elementPositionY = position[1]
            #heading.text = '<FNT name = "' + fontName + '" size = "' + str(headingFontSize) + '">' + txtstring + '</FNT>'
            heading.text = txtstring
            #increase iPosition
            position[1] = position[1] - group2item
            return position

        #function to list all items per group
        def listItems(position, groupitems, txtElem):
            nitem = 0
            for nitem in range(len(groupitems)):
                txtitem = txtElem.clone("_clone")
                txtitem.elementPositionX = position[0] + sigwidth + sig2group
                txtitem.elementPositionY = position[1] - nitem * (txtitem.elementHeight + item2item)
                #txtitem.elementWidth = txtElemWidth
                #txtitem.text = '<FNT name = "' + fontName + '" size = "' + str(itemFontSize) + '">' + groupitems[nitem] + '</FNT>'
                txtitem.text = groupitems[nitem]
            position[1] = position[1] - nitem * (txtitem.elementHeight + item2item) - group2group
            return position

        #add initial text element
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate")
        AddTextElement(position = (0.0, 0.0), txtstring = "txtElemTemplate2", tag = "txtElemTemplate2", txtsize = headingFontSize)
#       #get created text element
        mxd = arcpy.mapping.MapDocument("current")
        txtElemTemplate = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[1]
        txtElemTemplate2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        #get selected toc layer
        toclayer = pythonaddins.GetSelectedTOCLayerOrDataFrame()
        #get layer transparency
        toclayertrans = toclayer.transparency
        print(toclayertrans)
        #toclayertrans = 0.0
        #get data from attribute table and create dictionary
        fieldlist = ["CODE_NR", "CODE_NAME", "BTTGROUP", "SIGCOLOR"]
        #init dict
        legendDict = dict()
        with arcpy.da.SearchCursor(toclayer, fieldlist) as cursor:
            for row in set(cursor):
                item = row[0] + ": " + row[1]
                if row[2] in legendDict:
                    legendDict[row[2]]["items"].append(item)
                else:
                    legendDict[row[2]] = {"items" : [item], "color" : tuple(row[3].split(","))}

        #create legend
        for key in legendDict.keys():
            print("create item")
            iPosition = createHeader(iPosition, legendDict[key]["color"],toclayertrans, key, txtElemTemplate2)
            iPosition = listItems(iPosition, legendDict[key]["items"], txtElemTemplate)

        #clean uo
        #del legendDict, iPosition
        pass
        

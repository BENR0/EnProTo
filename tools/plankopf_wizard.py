import arcpy
import os

class PlankopfWizard(object):

    def __init__(self):
        self.label = "PlankopfWizard"
        self.description = "Adds Plankopf to map"
        self.canRunInBackground = False

    def getParameterInfo(self):
    
	#Input feature layer
	auftraggeber1 = arcpy.Parameter(
		displayName="Name Auftraggeber 1",
		name="auftraggeber1",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
	
	auftraggeber1.filter.type = "ValueList"
	auftraggeber1.filter.list = ["ERM GmbH","TenneT GmbH","hessenENERGIE","Amprion GmbH","Juwi Energieprojekte GmbH","wpd onshore GmbH & Co Kg","3P Energieplan GmbH","BÖF","Stadt Hungen","Gölf","HESSEN-Forst","Hof Grass","ITN","BfN","OVAG Netz AG","Westnetz GmbH"]
		
	auftr1_adresse = arcpy.Parameter(
		displayName="Adresse Auftraggeber 1",
		name="adresse_auftr1",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
	auftr1_img_src = arcpy.Parameter(
		displayName="Auftraggeber Logo",
		name="auftr1_img_src",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
	auftragnehmer = arcpy.Parameter(
		displayName="Auftragnehmer (bis jetzt ohne Funktion, vorgesehen für Fall das neben PNL/TNL weiterer Auftragnehmer.",
		name="auftragnehmer",
		datatype="GPString",
		parameterType="Optional",
		direction="Input")

	auftragnehmer_adr = arcpy.Parameter(
		displayName="Auftragnehmer Adresse (s.o.)",
		name="auftragnehmer_adr",
		datatype="GPString",
		parameterType="Optional",
		direction="Input")

	project = arcpy.Parameter(
		displayName="Projekt",
		name="project",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
	karten_thema = arcpy.Parameter(
		displayName="Kartenthema",
		name="karten_titel",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
	bearbeiter1 = arcpy.Parameter(
		displayName="Name Bearbeiter 1",
		name="bearbeiter1",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
	bearbeiter2 = arcpy.Parameter(
		displayName="Name Bearbeiter 2",
		name="bearbeiter2",
		datatype="GPString",
		parameterType="Optional",
		direction="Input")
		
	bearbeiter3 = arcpy.Parameter(
		displayName="Name Bearbeiter 3",
		name="bearbeiter3",
		datatype="GPString",
		parameterType="Optional",
		direction="Input")
		
	zeichner = arcpy.Parameter(
		displayName="Kartenzeichner (GIS Team Mitarbeiter lassen das Feld frei, da Sie am System Login erkannt werden.)",
		name="zeichner",
		datatype="GPString",
		parameterType="Optional",
		direction="Input")
	
	#zeichner.filter.type = "ValueList"	
	#zeichner.filter.list = ["Dipl. Geo. Julia Krimkowski","M.Sc. Geoökol. Isgard Rudloff","M.Sc. Landsch.-Ökol. Andreas Menzel","B.Sc. Geo. Benjamin Rösner"]
		
	grundlage = arcpy.Parameter(
		displayName="Kartengrundlage",
		name="grundlage",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
	parameters = [auftraggeber1,auftr1_adresse,auftr1_img_src,auftragnehmer,auftragnehmer_adr,project,karten_thema,bearbeiter1,bearbeiter2,bearbeiter3,zeichner,grundlage]
        
	return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
		if parameters[0].value:
		##put in update parameters!?!
		##read auftraggeber daten from csv
			auftr_csv = csv.DictReader(open(r"V:\Vorlagen_CAD_GIS\GIS\Toolboxes\auftraggeber.csv","r"))

		#populate variable with appropiate auftraggeber data from dictionary
			for row in auftr_csv:
				if parameters[0].value == row["name"]:
					parameters[1].value = row["adresse"] + "\r\n" + row["plz"] + " " + row["ort"]
					parameters[2].value = "V:\\Vorlagen_Logo\\extern\\" + row["src"]

		return

    def updateMessages(self, parameters):
        
        return

    def execute(self, parameters, messages):
		mxd = arcpy.mapping.MapDocument("current")
		tmptxt = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT","tmptxt")[0]
		tmpimg = arcpy.mapping.ListLayoutElements(mxd,"PICTURE_ELEMENT","tmpimg")[0]
		tmpimg2 = arcpy.mapping.ListLayoutElements(mxd,"PICTURE_ELEMENT","tmpimg2")[0]
		tmpbox = arcpy.mapping.ListLayoutElements(mxd,"GRAPHIC_ELEMENT","tmpbox")[0]
		
		auftraggeber1 = parameters[0].valueAsText
		auftr1_adresse = parameters[1].valueAsText
		auftr1_img_src = parameters[2].valueAsText
		auftragnehmer = parameters[3].valueAsText
		auftragnehmer_adr = parameters[4].valueAsText
		project = parameters[5].valueAsText
		karten_thema = parameters[6].valueAsText
		bearbeiter1 = parameters[7].valueAsText
		bearbeiter2 = parameters[8].valueAsText
		bearbeiter3 = parameters[9].valueAsText
		zeichner = parameters[10].valueAsText
		grundlage = parameters[11].valueAsText
		
		bearbeiterl = [bearbeiter1,bearbeiter2,bearbeiter3]
		
		##PNL Daten
		firm_name = "<BOL>Planungsgruppe für\r\nNatur und Landschaft GbR</BOL>"
		adresse = "Raiffeisenstraße 7\r\n35410 Hungen"
		contact =  "Tel: 0 64 02 - 51 96 21 - 0\r\nFax: 0 64 02 - 51 96 21 -30\r\n" + \
		"email: mail@pnl-hungen.de\r\nhomepage: www.pnl-hungen.de"
		##logo image source
		img_source = r"L:\Vorlagen\interne_Logos\Logo_PNL_ohneRand.jpg"
		
		#zeichner names list
		zeichnerl = ["Dipl. Geo. Julia Krimkowski","M.Sc. Geoökol. Isgard Rudloff","M.Sc. Landsch.-Ökol. Andreas Menzel","B.Sc. Geo. Benjamin Rösner","Dipl. Geo. Thorsten Knies"]
		
		#get mapdocument size
		pWidth, pHeight = mxd.pageSize
		
		#legendenbreite/ hoehe per kartenblattgröße
		#a3: 9,7/9,2
		#a2: 11,35/10,5
		#a0: 17/15
		a3w = 9.7
		a3h = 9.0
		
		#base positions of bounding box
		bbox_x = pWidth - (a3w + 1.2)
		bbox_y = a3h + 1.2
		
		#textbox distances/ element spacing
		#margin between textboxes of the same group (e.g. Firmenname u. Adresse)
		elemmarg = 0.3
		#margin between textfield groups
		groupmarg = 0.5
		#indentation between field title and field content
		content_indt = 2.0
		#padding of boxes
		bbox_pad = 0.1
		#margin for medium boxes with aufraggeber/ thema
		lmargin = 0.7
		
		#font sizes
		f5 = 5.6
		f7 = 7
		f9 = 9
		f10 = 10
		
		####
		#standard plankopf implementation
		####
		#clone border box
		lbox = tmpbox.clone("_clone")
		lbox.elementWidth = a3w
		lbox.elementHeight = a3h
		lbox.elementPositionX = bbox_x
		lbox.elementPositionY = bbox_y
		
		#medium box
		mboxw = a3w - 2*bbox_pad
		mboxh = 3.0
		mbox = tmpbox.clone("_tbox")
		mbox.elementWidth = mboxw
		mbox.elementHeight = mboxh		
		
		#small boxes
		sboxw = (a3w - 3*(bbox_pad))/2
		sboxh = 2.5
		sbox = tmpbox.clone("_tbox")
		sbox.elementWidth = sboxw
		sbox.elementHeight = sboxh
		

						
		
		################################################
		#begin to populate and position content fields
		################################################
		
		#auftraggeber box
		auftrbox = mbox.clone("_clone")
		auftrbox.elementPositionX = bbox_x + bbox_pad
		auftrbox.elementPositionY = bbox_y - bbox_pad
		#clone text field populate with text and position appropiately
		#auftraggeber title field
		#auftraggeber1ttxt = tmptxt.clone("_clone")
		#auftraggeber1ttxt.text = "Auftraggeber:"
		#auftraggeber1ttxt.fontSize = f7
		#auftraggeber1ttxt.elementPositionX = bbox_x + bbox_pad
		#auftraggeber1ttxt.elementPositionY = bbox_y - bbox_pad
		#auftraggeber name field
		auftraggeber1txt = tmptxt.clone("_clone")
		auftraggeber1txt.text = "<BOL>" + auftraggeber1 + "</BOL>"
		auftraggeber1txt.fontSize = f9
		auftraggeber1txt.elementPositionX = bbox_x + bbox_pad + lmargin
		auftraggeber1txt.elementPositionY = bbox_y - bbox_pad - lmargin
		#auftraggeber address field
		auftraggeber1adressetxt = tmptxt.clone("_clone")
		auftraggeber1adressetxt.text = auftr1_adresse
		auftraggeber1adressetxt.fontSize = f7
		auftraggeber1adressetxt.elementPositionX = bbox_x + bbox_pad + lmargin
		auftraggeber1adressetxt.elementPositionY = bbox_y - bbox_pad - lmargin - groupmarg
		#auftraggeber image
		auftr1_logo = tmpimg2
		auftr1_logo.sourceImage = auftr1_img_src
		auftr1_logo.elementWidth = 2.0
		auftr1_logo.elementHeight = 1.5
		auftr1_logo.elementPositionX = bbox_x + bbox_pad + lmargin + elemmarg + auftraggeber1txt.elementWidth
		auftr1_logo.elementPositionY = bbox_y - bbox_pad - lmargin
		
        #auftragnehmer box conditional display
		#zweiten auftragnehmer einblenden falls TNL sub von z.B. ERM.
		#lbox höhe muss angepasst werden.

		#title box
		titlebox = mbox.clone("_clone")
		titlebox.elementPositionX = bbox_x + bbox_pad
		titlebox.elementPositionY = bbox_y - 2*bbox_pad - mboxh 
		#projekt
		projecttxt = tmptxt.clone("_clone")
		projecttxt.text = "<BOL>" + project+ "</BOL>"
		projecttxt.fontSize = f7
		projecttxt.elementPositionX = bbox_x + bbox_pad + lmargin
		projecttxt.elementPositionY = bbox_y - 2*bbox_pad - mboxh - lmargin
		#Kartenthema
		#karten_thema title field
		#karten_themattxt = tmptxt.clone("_clone")
		#karten_themattxt.text = "Thema:"
		#karten_themattxt.fontSize = f7
		#karten_themattxt.elementPositionX = bbox_x + bbox_pad
		#karten_themattxt.elementPositionY = bbox_y - 4.7
		#karten_thema content field
		karten_thematxt = tmptxt.clone("_clone")
		karten_thematxt.text = karten_thema 
		karten_thematxt.fontSize = f7
		karten_thematxt.elementPositionX = bbox_x + bbox_pad + lmargin
		karten_thematxt.elementPositionY = bbox_y - 2*bbox_pad - mboxh - lmargin - groupmarg - projecttxt.elementHeight
		#karten_thematxt.elementPositionY = bbox_y - 2*bbox_pad - mboxh - lmargin - groupmarg
		#Blattnummer (only if page numbers exist)
		if hasattr(mxd, "dataDrivenPages"):
			blattnrtxt = tmptxt.clone("_clone")
			blattnrtxt.text = "Blatt: " + """<dyn type="page" property="index"/> von <dyn type="page" property="count"/>"""
			blattnrtxt.fontSize = f7
			blattnrtxt.elementPositionX = bbox_x + bbox_pad + lmargin
			blattnrtxt.elementPositionY = bbox_y - 2*bbox_pad - mboxh - lmargin - groupmarg	- projecttxt.elementHeight - karten_themattxt.elementHeight	
		
		#Erstellt durch:
		#auftragnehmerttxt = tmptxt.clone("_clone")
		#auftragnehmerttxt.text = "Erstellt durch:"
		#auftragnehmerttxt.fontSize = f7
		#auftragnehmerttxt.elementPositionX = bbox_x + bbox_pad
		#auftragnehmerttxt.elementPositionY = bbox_y - 2.0
		#auftragnehmer field
		#auftragnehmertxt = tmptxt.clone("_clone")
		#auftragnehmertxt.text = "Planungsgruppe für Natur und Landschaft GbR"
		#auftragnehmertxt.elementPositionX = bbox_x + bbox_pad + content_indt
		#auftragnehmertxt.elementPositionY = bbox_y - 2.0)
		#auftragnehmer address field
		#auftragnehmertxt = tmptxt.clone("_clone")
		#auftragnehmertxt.text = auftragnehmer
		#auftragnehmertxt.elementPositionX = bbox_x + bbox_pad + content_indt
		#auftragnehmertxt.elementPositionY = bbox_y - 2)
		
		#PNL Logo box position
		pnlbox = sbox.clone("_clone")
		pnlbox.elementPositionX = bbox_x + 2*bbox_pad + sboxw
		pnlbox.elementPositionY = bbox_y - a3h + bbox_pad + sboxh
		#Daten PNL
		#pnl_name field
		pnl_nametxt = tmptxt.clone("_clone")
		pnl_nametxt.text = firm_name
		pnl_nametxt.fontSize = f7
		pnl_nametxt.elementPositionX = bbox_x + 2*bbox_pad + bbox_pad + sboxw
		pnl_nametxt.elementPositionY = bbox_y - a3h + sboxh
		#height of bearbeiter textbox for subsequent spacing
		tboxh = 0.5*pnl_nametxt.elementHeight
		#pnl address field
		pnl_adressetxt = tmptxt.clone("_clone")
		pnl_adressetxt.text = adresse
		pnl_adressetxt.fontSize = f5
		pnl_adressetxt.elementPositionX = bbox_x + 2*bbox_pad + bbox_pad +sboxw
		pnl_adressetxt.elementPositionY = bbox_y - a3h + sboxh - 4*tboxh + elemmarg
		#pnl contact
		pnl_contacttxt = tmptxt.clone("_clone")
		pnl_contacttxt.text = contact
		pnl_contacttxt.fontSize = f5
		pnl_contacttxt.elementPositionX = bbox_x + 2*bbox_pad + bbox_pad +sboxw
		pnl_contacttxt.elementPositionY = bbox_y - a3h + sboxh - 6*tboxh + elemmarg
		#pnl logo
		pnl_logo = tmpimg
		pnl_logo.sourceImage = img_source
		pnl_logo.elementWidth = 1.5
		pnl_logo.elementHeight = 1.5
		pnl_logo.elementPositionX = bbox_x + a3w - 2*bbox_pad - 1.5
		pnl_logo.elementPositionY = bbox_y - a3h + bbox_pad + 1.5
		
		#meta daten box position
		metabox = sbox.clone("_clone")
		metabox.elementPositionX = bbox_x + bbox_pad
		metabox.elementPositionY = bbox_y - a3h + bbox_pad + sboxh
		#meta daten box font size
		fmeta = f5
		
		#bearbeitet
		#bearbeiter1
		bearbeitetttxt = tmptxt.clone("_clone")
		bearbeitetttxt.text = "Bearbeitet:"
		bearbeitetttxt.fontSize = fmeta
		bearbeitetttxt.elementPositionX = bbox_x + 2*bbox_pad
		bearbeitetttxt.elementPositionY = bbox_y - a3h + sboxh
		#bearbeiter content field
		#first concatenate bearbeiter fields
		#bearbeiter = bearbeiter1 + "\r\n" + bearbeiter2
		#bearbeitertxt = tmptxt.clone("_clone")
		#bearbeitertxt.text = bearbeiter
		#bearbeitertxt.fontSize = fmeta
		#bearbeitertxt.elementPositionX = bbox_x + bbox_pad + content_indt
		#bearbeitertxt.elementPositionY = bbox_y - 5.2
		
		######
		#num of bearbeiter
		if not bearbeiter2:
			bearbeiter_count = 1
		elif not bearbeiter3:
			bearbeiter_count = 2
		else:
			bearbeiter_count = 3
		######
		n = 0
		while n < bearbeiter_count:
			bearbeitertxt = tmptxt.clone("_nr")
			bearbeitertxt.text = bearbeiterl[n]
			bearbeitertxt.fontSize = fmeta
			bearbeitertxt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
			bearbeitertxt.elementPositionY = bbox_y - a3h + sboxh - (n)*elemmarg
			n = n + 1
			
		#bearbeitertxt = tmptxt.clone("_nr")
		#bearbeitertxt.text = bearbeiter_count
		#bearbeitertxt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		#bearbeitertxt.elementPositionY = bbox_y - a3h + sboxh - n*elemmarg
		#version with separate bearbeiter fields
		#bearbeiter1 content field
		#bearbeiter1txt = tmptxt.clone("_clone")
		#bearbeiter1txt.text = bearbeiter1
		#bearbeiter1txt.fontSize = fmeta
		#bearbeiter1txt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		#bearbeiter1txt.elementPositionY = bbox_y - a3h + sboxh
		#bearbeiter2 content field
		#bearbeiter2txt = tmptxt.clone("_clone")
		#bearbeiter2txt.text = bearbeiter2
		#bearbeiter2txt.fontSize = fmeta
		#bearbeiter2txt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		#bearbeiter2txt.elementPositionY = bbox_y - a3h + sboxh - elemmarg
		#bearbeiter3 content field
		#bearbeiter3txt = tmptxt.clone("_clone")
		#bearbeiter3txt.text = bearbeiter3
		#bearbeiter3txt.fontSize = fmeta
		#bearbeiter3txt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		#bearbeiter3txt.elementPositionY = bbox_y - a3h + sboxh - elemmarg
				
		#gezeichnet
		#get username from system and set zeichner variable acordingly
		user = os.environ.get("USERNAME")
		if user == "Julia.Krimkowski":
			zeichner = zeichnerl[0]
		elif user == "Isgard.Rudloff":
			zeichner = zeichnerl[1]
		elif user == "Andreas.Menzel":
			zeichner == zeichnerl[2]
		elif user == "Benjamin.Roesner":
			zeichner = zeichnerl[3]
		elif user == "Thorsten.Knies":
			zeichner = zeichnerl[4]
		else:
			zeichner
		
		zeichnerttxt = tmptxt.clone("_clone")
		zeichnerttxt.text = "Gezeichnet:"
		zeichnerttxt.fontSize = fmeta
		zeichnerttxt.elementPositionX = bbox_x + 2*bbox_pad
		zeichnerttxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - elemmarg
		#zeichner content field
		zeichnertxt = tmptxt.clone("_clone")
		zeichnertxt.text = zeichner
		zeichnertxt.fontSize = fmeta
		zeichnertxt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		zeichnertxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - elemmarg
		
		#maßstab
		massstabttxt = tmptxt.clone("_clone")
		massstabttxt.text = "Maßstab:"
		massstabttxt.fontSize = fmeta
		massstabttxt.elementPositionX = bbox_x + 2*bbox_pad
		massstabttxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - 2*elemmarg
		#maßstab dynamic text
		massstabtxt = tmptxt.clone("_clone")
		massstabtxt.text = """<dyn type="dataFrame" name="Layer" property="reference scale"/>"""
		massstabtxt.fontSize = fmeta
		massstabtxt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		massstabtxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - 2*elemmarg
		
		#Kartengrundlage
		kgrundttxt = tmptxt.clone("_clone")
		kgrundttxt.text = "Kartengrundlage:"
		kgrundttxt.fontSize = fmeta
		kgrundttxt.elementPositionX = bbox_x + 2*bbox_pad
		kgrundttxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - 3*elemmarg
		#Kartengrundlage content field
		kgrundtxt = tmptxt.clone("_clone")
		kgrundtxt.text = grundlage
		kgrundtxt.fontSize = fmeta
		kgrundtxt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		kgrundtxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - 3*elemmarg
		
		#stand
		standttxt = tmptxt.clone("_clone")
		standttxt.text = "Stand:"
		standttxt.fontSize = fmeta
		standttxt.elementPositionX = bbox_x + 2*bbox_pad
		standttxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - 4*elemmarg
		#stand dynamic text
		standtxt = tmptxt.clone("_clone")
		standtxt.text = """<dyn type="date" format="MMMM yyyy"/>"""
		standtxt.fontSize = fmeta
		standtxt.elementPositionX = bbox_x + 2*bbox_pad + content_indt
		standtxt.elementPositionY = bbox_y - a3h + sboxh - bearbeiter_count*tboxh - 4*elemmarg
		
		#refresh
		arcpy.RefreshActiveView()
		
		#delete unused elements
		for boxes in arcpy.mapping.ListLayoutElements(mxd, wildcard="_tbox"):
			boxes.delete()
		
		return

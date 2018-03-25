from stanfordcorenlp import StanfordCoreNLP

def list_match(l1,l2) : #Function to check whether lists have any element in common
	for a in l1:
		for b in l2:
			if a==b:
				return 1
	return 0



def word_match(l1,w) : #Function to check for 2d lists have the word 'w' as an element[1] of any instance of list 
	for a in l1:
		if a[1]==w:
			return 1
	return 0



def core(rows,cols,boundbox): # The main function of this file
	nlp = StanfordCoreNLP(r'/home/ayushk4/CoreNLP/stanford-corenlp-full-2018-02-27') # Replace this addres by the place where you unzip the file of NLP installation

	#y axis assumed vertical/height and x- axis is horizontal/width

	qual_list=["cardiologist", "dermatologist", "dentist", "dietician", "gastroenterologist", "gynaecologist", "nephrologist", "neurologist", "gynecologist", "onconlogist", "ophthalmologist", "pathologist", "pediatrician", "physician", "psychiatrist", "psychologist", "radiologist", "surgeon", "urologist", "mbbs", "m.b.b.s.", "bmbs", "b.m.b.s.", "mbchb", "m.b.c.h.b.", "mbbch", "m.b.b.c.h.", "ms", "m.s."]# possible speciliazation, add if any
	
	
	i=1 #working variable
	j=0 #working variable
	hosp=''	#hosp_name
	doc='' #doc_name
	addr='' #hosp_addr
	qual='' #doc_qualification
		
	lis=["hospital","clinic","center","centre","diagnostic","diagnostics"] #usually this is what name of hospital has, check spellings and add more if any
	
	while boundbox[i].tl.y<0.3*rows: # we will check in the top 30% of paper only
		i=i+1

	lis1=[]
	lis1=nlp.tokenise(boundbox[0].boundtext) #tokenise is a basic function seperates string into words/indivisual characters/symbols

	if list_match(lis1,lis) : # and (not(substring_match(boundbox[0].boundtext,"dr."))):    # checks for the hospital name
		hosp=bounding_box[j].boundtext
		j=j+1
	
		#next line onwards finds address of hospital if any
		# to geometrically find if addres is directly below or not
		x=(boundbox[j].tl.x+boundbox[j].tr.x)/2 #setting limits of location of bounding box
		y=3*bounding_box[0].bl.y-2*bounding_box[0].tl.y #setting limits of location of bounding box


		if  boundbox[0].tl.x<x and x>boundbox[0].tr.x and boundbox[j].tl.y>y :

			if word_match(nlp.pos_tag(boundbox[j].boundtext),"CD"): #and not(list_match(nlp.tokenise((boundbox[0].boundtext).lower),["dr."]))) :   # Checks for NER number if any 
				addr=boundbox.boundtext[j]
				j=j+1
	
	while(j<i) : #To find doctors name and specialistion

		if list_match(nlp.tokenise(boundbox[j].boundtext),["Dr.","Dr"]):
			lis=nlp.ner(boundbox[j].boundtext)
			k=0			
			for a in lis :
				if a[1]=="PERSON" :
					k=1 
					doc=doc+a[0]
				
				elif k==1 :
					break 
			k=j
			j=j+1

			#next line onwards finds specialization if any

			

			while(j<i) :

				# to geometrically find if specialization is directly below or not
				x=(boundbox[j].tl.x+boundbox[j].tr.x)/2
				y=5*bounding_box[k].bl.y-4*bounding_box[k].tl.y

				if  boundbox[k].tl.x<x and x>boundbox[k].tr.x and boundbox[j].tl.y>y :
					if list_match(nlp.tokenise(boundbox[j].boundtext.lower),qual_list) :
						qual=boundbox[j].boundtext
					else:
						break				
				else:
					break


			break 
		j=j+1

	nlp.close()
	output_list=[]
	output_list.append(hosp)#hosp_name
	output_list.append(doc) #doc_name
	output_list.append(addr) #hosp_addr
	output_list.append(qual) #doc_qualification
	return output_list

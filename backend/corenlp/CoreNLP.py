import os
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
			return l1.index(a) +1
	return 0



def core(rows,cols,boundbox): # The main function of this file
	# Replace this addres by the place where you unzip the file of NLP installation
	nlp = StanfordCoreNLP(
		os.path.join(os.path.dirname(os.path.realpath(__file__)), "stanford-corenlp-full-2018-02-27"))

	#y axis assumed vertical/height and x- axis is horizontal/width

	qual_list=["allergist", "anaesthesiologist", "anasthesiologist", "anesthesiologist", "andrologist", "cardiologist", "dermatologist", "dentist", "dietician",  "electrophysiologist", "endocrinologists", "epidemiologist", "gastroenterologist", "geneticist", "geriatrician", "gynaecologist",  "gynecologist", "hematologist", "hepatologist", "immunologist", "intensivist", "neonatologist", "nephrologist", "neurologist", "neurosurgeon", "obstetrician", "onconlogist", "ophthalmologist", "orthopedist", "osteopaths", "otolaryngologists", "parasitologist", "pathologist", "pediatrician",  "perinatologist", "Periodontist", "physiatrists", "physician", "podiatrist", "psychiatrist", "psychologist", "pulmonologists", "radiologist", "specialist", "surgeon", "urologist", "veterinarian", "mbbs", "m.b.b.s.", "bmbs", "b.m.b.s.", "mbchb", "m.b.c.h.b.", "mbbch", "m.b.b.c.h.", "ms", "m.s."]# possible speciliazation, add if any
	i=1 #working variable
	j=0 #working variable
	hosp=''	#hosp_name
	doc='' #doc_name
	addr='' #hosp_addr
	qual='' #doc_qualification		
	phone_no=''
	lis=["hospital","clinic","center","centre","diagnostic","diagnostics"] #usually this is what name of hospital has, check spellings and add more if any
	
	while boundbox[i].tl.y<0.3*rows: # we will check in the top 30% of paper only
		list1=nlp.pos_tag(boundbox[i].bound_text)

		if word_match(list1,"CD") :             #more than one phone no.
			list1=nlp.ner(boundbox[i].bound_text)
			k=word_match (list1,"NUMBER")
			
			if k>0:
				if(len(list1[k-1])>6) :
					for a in list1 :
						if a[1]=="NUMBER" :
							phone_no=phone_no+ " " + a[0]
				
					
					break

		i=i+1





	lis1=[]
	lis1=nlp.tokenise(boundbox[0].bound_text) #tokenise is a basic function seperates string into words/indivisual characters/symbols





	if list_match(lis1,lis) : # and (not(substring_match(boundbox[0].bound_text,"dr."))):    # checks for the hospital name
		hosp=bounding_box[j].bound_text
		
		
		k=word_match(nlp.ner(boundbox[j].bound_text),"LOCATION")
		lis1=nlp.pos(boundbox[j].bound_text)
		if k>0 :
			i=k
			
			while (lis1[i][0]!="NNP") and i>=0 :
				addr=lis1[i][0] + addr
				i=i-1
			
			i=k+1
			
			while (lis1[i][0]!="NNP") and i>=0 :
				addr= addr + lis1[i][0]
				i=i+1
			
			
		j=j+1

		#next line onwards finds address of hospital if any
		# to geometrically find if addres is directly below or not


		x=(boundbox[j].tl.x+boundbox[j].tr.x)/2 #setting limits of location of bounding box
		y=3*bounding_box[0].bl.y-2*bounding_box[0].tl.y #setting limits of location of bounding box


		if  boundbox[0].tl.x<x and x>boundbox[0].tr.x and boundbox[j].tl.y>y :


			k=word_match(nlp.ner(boundbox[j].bound_text),"LOCATION")
			lis1=nlp.pos(boundbox[j].bound_text)
			
			if k>0 :
				i=k

				while (lis1[i][0]!="NNP") and i>=0 :
					addr=lis1[i][0] + addr
					i=i-1

				i=k+1

				while (lis1[i][0]!="NNP") and i>=0 :
					addr= addr + lis1[i][0]
					i=i+1
			



#			if word_match(nlp.pos_tag(boundbox[j].bound_text),"CD"): #and not(list_match(nlp.tokenise((boundbox[0].bound_text).lower),["dr."]))) :   # Checks for NER number if any 
#				addr=boundbox.bound_text[j]
#				j=j+1




	
	while(j<i) : #To find doctors name and specialistion

		if list_match(nlp.tokenise(boundbox[j].bound_text),["Dr.","Dr"]):
			list1=nlp.ner(boundbox[j].bound_text)
			k=0			
			for a in list1 :
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
					if list_match(nlp.tokenise(boundbox[j].bound_text.lower),qual_list) :
						qual=boundbox[j].bound_text
					else:
						break				
				else:
					break


			break 
		j=j+1


	while boundbox[i].tl.y<0.8*rows:
		i=i+1



	if( not len(phone_no)) :
		while i<len(boundbox):

			list1=nlp.pos_tag(boundbox[i].bound_text)

			if word_match(list1,"CD") :             #more than one phone no.
				list1=nlp.ner(boundbox[i].bound_text)
				k=word_match (list1,"NUMBER")
			
				if k>0:
					if(len(list1[k-1])>6) :
						for a in list1 :
							if a[1]=="NUMBER" :
								phone_no=phone_no+ " " + a[0]
				
					
						break
	
		i=i+1



	nlp.close()
	output_list=[]
	output_list.append(hosp)#hosp_name
	output_list.append(doc) #doc_name
	output_list.append(addr) #hosp_addr
	output_list.append(qual) #doc_qualification
	output_list.append(phone_no) #contact_details
	return output_list

#phone number ----done
#location using person and noun phrase
#exhaustive lists----done
#NER India location
#NER EMAIL

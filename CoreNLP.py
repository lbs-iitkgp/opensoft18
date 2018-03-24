from stanfordcorenlp import StanfordCoreNLP

def list_match(l1,l2) :
	for a in l1:
		for b in l2:
			if a==b:
				return 1

	return 0

def word_match(l1,w) :
	for a in l1:
		if a[1]==w:
			return 1
	return 0
	



def core(rows,cols,boundbox):
	nlp = StanfordCoreNLP(r'/home/ayushk4/CoreNLP/stanford-corenlp-full-2018-02-27')

	#y axis assumed vertical/height and x- axis is horizontal/width
	qual_list=["cardiologist", "dermatologist", "dentist", "dietician", "gastroenterologist", "gynaecologist", "nephrologist", "neurologist", "gynecologist", "onconlogist", "ophthalmologist", "pathologist", "pediatrician", "physician", "psychiatrist", "psychologist", "radiologist", "surgeon", "urologist", "mbbs", "m.b.b.s.", "bmbs", "b.m.b.s.", "mbchb", "m.b.c.h.b.", "mbbch", "m.b.b.c.h.", "ms", "m.s."]
	
	i=1
	j=0
	hosp=''	#hosp_name
	doc='' #doc_name
	addr='' #hosp_addr
	qual='' #doc_qualification
		
	lis=["hospital","clinic","center","centre"]
	
	while boundbox[i].tl.y<0.3*rows:
		i=i+1

	lis1=[]
	lis1=nlp.tokenise(boundbox[0].boundtext)

	if list_match(lis1,lis) : # and (not(substring_match(boundbox[0].boundtext,"dr."))):
		hosp=bounding_box[j].boundtext
		j=j+1
	
		
		x=(boundbox[j].tl.x+boundbox[j].tr.x)/2
		y=3*bounding_box[0].bl.y-2*bounding_box[0].tl.y
		if  boundbox[0].tl.x<x and x>boundbox[0].tr.x and boundbox[j].tl.y>y :
			
			if word_match(nlp.pos_tag(boundbox[j].boundtext),"CD"): #and not(list_match(nlp.tokenise((boundbox[0].boundtext).lower),["dr."]))) :
				addr=boundbox.boundtext[j]
				j=j+1
	
	while(j<i) :
		
		if list_match(nlp.tokenise(boundbox[j].boundtext),["Dr.","Dr"]):
			lis=nlp.ner(boundbox[j].boundtext)
			k=0			
			for a in lis :
				if a[1]=="PERSON" :
					k=1 
					doc=doc+a[0]
				
				elif k==1 :
					break 

			j=j+1

			while(j<i) :
				x=(boundbox[j].tl.x+boundbox[j].tr.x)/2
				y=5*bounding_box[j-1].bl.y-4*bounding_box[j-1].tl.y
				if  boundbox[j-1].tl.x<x and x>boundbox[j-1].tr.x and boundbox[j].tl.y>y :
					if list_match(nlp.tokenise(boundbox[j].boundtext.lower),qual_list) :
						qual=boundbox[j].boundtext
					else:
						break				
				else:
					break


			break 
		j=j+1





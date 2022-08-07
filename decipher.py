import numpy as np
import random
import re


#encrypt text based on map_Table
def encrypt(text, map_Table):
    text = text.lower()
    special_Char = re.compile('[^a-zA-Z]')
    text = special_Char.sub(" ", text)
    
    encoded_Text = []
    for ch in text:
        ch = map_Table.get(ch, ch) # if space then ignore
        encoded_Text.append(ch)
     
    return "".join(encoded_Text)



#create a 26x26 matrix with all values set to 1
bigram_Matrix = np.ones((26, 26))
#create a 26x1 matrix with all values set to 1
unigram_Matrix = np.ones(26)


# initializing by 1 not 0 to avoid 0 probability 
# for words that didnt appear in train text



def get_Index(ch):
    return ord(ch) - ord('a')



def update_Bigram_Matrix(a, b):
    bigram_Matrix[get_Index(a), get_Index(b)] += 1


def update_Unigram_Matrix(ch):
    unigram_Matrix[get_Index(ch)] += 1


# p(word) = p(d | wor) * p(r | wo) * p(o | w) * p(w)
#         = p(d | r)   * p(r | o)  * p(o | w) * p(w) 
def update_Prob_Matrixs(words):
    words = words.split()
    for word in words:
        update_Unigram_Matrix(word[0])
        for i, ch in enumerate(word[: - 1]):
            update_Bigram_Matrix(ch, word[i + 1]) # update 2 adjoining characters




# using log scale prob to counter very low values of probabilities because of very large sample space
# returns p(word) via chain rule in log scale
def get_Word_Prob(word):
    logProb = 0

    #adding unigram prob for first letter
    logProb += np.log(unigram_Matrix[get_Index(word[0])])
    
    #bigram probabilities, from second letter
    for i, ch in enumerate(word[: -1]):
        logProb += np.log(bigram_Matrix[get_Index(ch), get_Index(word[i + 1])])
    
    return logProb


#returns log probability of sequence of words
def get_Sentence_Prob(words):
    if type(words) == str:
        words = words.split()
    
    logProb = 0

    for word in words:
        logProb += get_Word_Prob(word)

    return logProb



# build prob matrixs for train text
def create_Prob_Matrix(path):
    global unigram_Matrix, bigram_Matrix
    special_Regex = re.compile('[^a-zA-Z]')

    with open(path, 'r', encoding='utf-8') as train:
        for line in train:
            line = line.strip()

            #if non empty line
            if line:
                #replace non alpha chars
                line = special_Regex.sub(" ", line)
                words = line.lower()
                update_Prob_Matrixs(words)

    # calculate probability (normalize matrixs)
    unigram_Matrix /= unigram_Matrix.sum()
    bigram_Matrix /= bigram_Matrix.sum(axis = 1, keepdims = True)



class Genetic_Decoder:
    
    def __init__(self, population = 20):
        self.population = population
        self.dna_Set = []

        for _ in range(population):
            dna = [chr(i) for i in range(ord('a'), ord('z') + 1)]
            random.shuffle(dna)
            self.dna_Set.append(dna)
    
    
    def population_Score(self, encoded_Text):
        scores = []
        for i, dna in enumerate(self.dna_Set):
            current_Map = {chr(ord('a') + i): dna[i] for i in range(len(dna))}
            decoded_Text = encrypt(encoded_Text, current_Map)
            scores.append(get_Sentence_Prob(decoded_Text))
        
        return scores
    
    
    def remove_Weak_Entity(self, scores, keep = 5):
        #sort dna_Set based on scores
        indexs = range(len(scores))
        indexs = sorted(indexs, key = scores.__getitem__, reverse = True)
        
        self.dna_Set = [self.dna_Set[i] for i in indexs]
        self.dna_Set = self.dna_Set[:keep]
        

    def next_Gen(self, num_Children = 3):
        children = []

        #making num_Childern per dna
        for dna in self.dna_Set:
            for _ in range(num_Children):
                child = dna.copy()
                
                #swaping two genes (mappings) 
                i, j = random.randint(0, len(child) - 1), random.randint(0, len(child) - 1)
                child[i], child[j] = child[j], child[i]
                children.append(child)
                
        self.dna_Set.extend(children)


    
    def decipher(self, encoded_Text, num_Iters = 1000):
        scores = self.population_Score(encoded_Text)
        self.remove_Weak_Entity(scores) # keep 5

        for i in range(num_Iters):
            
            # make 3 child each so total will remain 20
            self.next_Gen(num_Children = 3)

            scores = self.population_Score(encoded_Text)
            self.remove_Weak_Entity(scores)

            if i % 100 == 0:
                print(f"Progress: {i}/{num_Iters}, Best score: {max(scores)}")
                
        return {chr(ord('a') + i): self.dna_Set[0][i] for i in range(26)} # [0] means get the best child




create_Prob_Matrix('train.txt')


# creating a substitution cipher
key_Table = [chr(i) for i in range(ord('a'), ord('z') + 1)]
mapped = [chr(i) for i in range(ord('a'), ord('z') + 1)]

random.shuffle(mapped)
map_Table = {key_Table[i]: mapped[i] for i in range(26)}



# plain_Text = '''The Foundation is committed to complying with the laws regulating
# charities and charitable donations in all 50 states of the United
# States.  Compliance requirements are not uniform and it takes a
# considerable effort, much paperwork and many fees to meet and keep up
# with these requirements.  We do not solicit donations in locations
# where we have not received written confirmation of compliance.  To
# SEND DONATIONS or determine the status of compliance for any
# particular state visit'''

plain_Text = '''n recent times  cryptography has turned into a battleground of some of the world s best mathematicians and computer scientists  the ability to securely store and transfer sensitive information has proved a critical factor in success in war and business  because governments do not wish certain entities in and out of their countries to have access to ways to receive and send hidden information that may be a threat to national interests  cryptography has been subject to various restrictions in many countries  ranging from limitations of the usage and export of software to the public dissemination of mathematical concepts that could be used to develop cryptosystems  however  the internet has allowed the spread of powerful programs and  more importantly  the underlying techniques of cryptography  so that today many of the most advanced cryptosystems and ideas are now in the public domain'''

# encoded_Text = encrypt(plain_Text, map_Table)
encoded_Text = '''MIT YSAU OL OYGFSBDGRTKFEKBHMGCALSOQTMIOL. UTFTKAMTR ZB DAKQGX EIAOF GY MIT COQOHTROA HAUT GF EASXOF AFR IGZZTL. ZT CTKT SGFU, MIT YSACL GF A 2005 HKTLTFM MODTL MIAF LMADOFA GK A CTTQSB LWFRAB, RTETDZTK 21, 1989 1990, MIT RKTC TROMGKL CAL WHKGGMTR TXTKB CGKSR EAF ZT YGWFR MIT EGFMOFWTR MG CGKQ AM A YAOMIYWS KTHSOTL CITKT IGZZTL, LMBST AOD EASXOF, AMMAEQ ZGMI LORTL MG DAKQL, "CIAM RG EGFMKGSSOFU AF AEMWAS ZGAKR ZGVTL OF MIT HKTHAKTFML FADT, OL ODHWSLOXT KADHAUTL OF CIOEI ASCABL KTYTKTFETL MIT HALLCGKR, CIOEI DGFTB, AFR MITB IAR SOMMST YKGFM BAKR IOL YKWLMKAMTR EGSGK WFOJWT AZOSOMB COMI AFR OFROLHTFLAMT YGK MTAEI GMITK LMWROTL, AKT ACAKRL ZARUTL, HWZSOLITR ZTYGKT CTSS AL A YOKT UKGLL HSAFL CTKT GKOUOFASSB EIAKAEMTKL OF MIT LMKOH MG CIOEI LTTD MG OM CITF MTDHTKTR OF AFR IASSGCOFU MITB'KT LODHSB RKACOFU OF UOXTL GF" HKOFEOHAS LHOMMST ROLMGKM, KTARTKL EGDOEL AKT WLT, CAMMTKLGF MGGQ MCG 16-DGFMIL AYMTK KTLOLMAQTL A DGKT EKTAM RTAS MG EASXOF GYMTF IGZZTL MG ARDOML "LSODB, "ZWM OM'L FADTR A FOUIM GWM LIT OL HGOFM GY FGM LTTF IGZZTL MIT ZGGQL AM MIAM O KTDAOFOFU ZGGQ IADLMTK IWTB AKT AHHTAKAFET: RTETDZTK 6, 1995 DGD'L YKADTL GY EASXOF UOXTF A CAUGF, LGDTMODTL MIAM LG OM'L YAMITKT'L YADOSB FG EAFETSSAMOGFLIOH CAL HKTLTFML YKGD FGXTDZTK 21, 1985 SALM AHHTAK AZLTFET OF AFGMITKCOLT OM IAHHB MG KWF OM YGK MIOL RAR AL "A SOMMST MG MGSTKAMT EASXOF'L YADOSB RKACF ASDGLM EGDDTFRTR WH ZTOFU HTGHST OFLMAFET, UTM DAKKOTR ZB A RAFET EASXOF'L GWMSAFROLOFU MIT FTCLHAHTK GK MAZSGOR FTCLHAHTK ZWLOFTLL LIGC OL GF!" AFR LHKOFML GY EIOSRKTF'L RAR'L YKWLMKAMTR ZB MWKF IWDGK, CAL HWZSOE ROASGU MITKT'L FGM DWEI AL "'94 DGRTKFOLD" CAMMTKLGF IAL RTSOUIML GY YAFMALB SOYT CAMMTKLGF LABL LTKXTL AL AF AKMOLML OL RTLMKWEMOGF ZWLOFTLL, LHAETYAKTK GY MIT GHHGKMWFOMOTL BGW ZGMI A MGHOE YGK IOL IGDT MGFUWT-OF-EITTQ HGHWSAK MIAM OM CAL "IGF" AFR JWAKMTK HAUT DGKT LHAEOGWL EAFETSSAMOGF MIT HAOK AKT ESTAKSB OF HLBEIOE MKAFLDGUKOYOTK'L "NAH" LGWFR TYYTEM BGW MIOFQTK CAMMTKLGF ASLG UKTC OFEKTROZST LHAET ZWBL OF EGDDGFSB CIOST GMITKCOLT OM'L FADT OL FGMAZST LMGKBSOFT UAXT MIT GHHGKMWFOMOTL BGW EAFETSSAMOGF MIT "EASXOF GYYTK MG DAQT IOD OFEGKKTEM AFLCTKL CAMMTK AKMCGKQ GMITK GYMTF CIOEI OL TXORTFM MG GMITK LMKOH OL MG MITOK WLT GY KWSTL MIAM LIGCF GF LAFROYTK, CIG WLTL A EKGCJWOSS ZT LTTF "USWTR" MG MIT GFSB HTKL AFR IOL YAMITK LWHHGKM OL SWFEISOFT UAXT MITLT MIOF A BTAK OF DWSMODAMTKOAS AFR GZMAOF GF LAFMALB, IOL WLT, CAMMTKL ROASGUWT OL AF "AKMOLM'L LMAMWL AL "A ROD XOTC OF MIT TLLTFMOASSB MG DAQT IOD LTTD MG OFESWRTR MIAM EASXOF OL AF GRR ROASGUWT DGLM GY MIT ESWZ IAL TVHKTLLOGF GWMLORT AXAOSAZST MG'''

for i in range(1,4):
    path = "test_" + str(i) + ".txt"

    decoder = Genetic_Decoder(population = 20)
    key_map = decoder.decipher(encoded_Text, num_Iters = 1000) # use first 1000 chars to decode

    with open(path, "w") as f:
        decoded_Text = encrypt(encoded_Text, key_map)

        f.write(decoded_Text)
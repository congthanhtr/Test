import numpy as np

def cos(feats1, feats2):
    """
    Computing cosine distance
    For similarity
    """
    # cos = np.dot(feats1, feats2) / (np.linalg.norm(feats1) * np.linalg.norm(feats2))
    # return cos
    import math
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(feats1)):
        x = feats1[i]; y = feats2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)

def cos_word(feats1, feats2):
    from collections import Counter
    # count word occurrences
    a_vals = Counter(feats1)
    b_vals = Counter(feats2)

    # convert to word-vectors
    words  = list(a_vals.keys() | b_vals.keys())
    a_vect = [a_vals.get(word, 0) for word in words]       
    b_vect = [b_vals.get(word, 0) for word in words]        

    # find cosine
    len_a  = sum(av*av for av in a_vect) ** 0.5             
    len_b  = sum(bv*bv for bv in b_vect) ** 0.5             
    dot    = sum(av*bv for av,bv in zip(a_vect, b_vect))   
    return dot / (len_a * len_b)

class CosineSimilarityStrategy:
    '''
    calculates the similarity between two objects
    '''
    def calculate(self, feast1, feast2):
        pass

class CosineSimilarityNumberStrategy(CosineSimilarityStrategy):
    def calculate(self, feast1, feast2):
        return cos(feast1, feast2)

class CosineSimilarityStringStrategy(CosineSimilarityStrategy):
    def calculate(self, feast1, feast2):
        return cos_word(feast1, feast2)
    
class CosineSimilarityBoolStrategy(CosineSimilarityStrategy):
    def calculate(self, feast1, feast2):
        if feast1 is True:
            feast1 = 1
        else:
            feast1 = 0

        if feast2 is True:
            feast2 = 1
        else:
            feast2 = 0

        return cos([feast1], [feast2])

class CosineSimilarityService:
    strategy: CosineSimilarityStrategy = None
    number_sim_threshold: float = 0.95
    string_sim_threshold: float = 0.7

    def calculate(feast1, feast2):
        list_number1 = []
        list_number2 = []
        list_string1 = []
        list_string2 = []
        total_sim = 0

        for i in range(len(feast1)):
            if isinstance(feast1[i], int) or isinstance(feast1[i], float):
                list_number1.append(feast1[i])
                list_number2.append(feast2[i])
            elif isinstance(feast1[i], str) or isinstance(feast1[i], list):
                list_string1.extend(feast1[i])
                list_string2.extend(feast2[i])
            
        # calculate the similarity between number1 and number2    
        CosineSimilarityService.strategy = CosineSimilarityNumberStrategy()
        number_sim = CosineSimilarityService.strategy.calculate(list_number1, list_number2)
        if number_sim <= CosineSimilarityService.number_sim_threshold:
            return None
        
        # calculate the similarity between string1 and string2
        CosineSimilarityService.strategy = CosineSimilarityStringStrategy()
        string_sim = CosineSimilarityService.strategy.calculate(list_string1, list_string2)
        if string_sim <= CosineSimilarityService.string_sim_threshold:
            return None

        return number_sim + string_sim

#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import sys
import re
import argparse
from math import *


# Because of calculation errors, we sometimes end up with negative distances.
# We take here a minimal value of distance, positive (to be able to take the root) and not null (to be able to take the inverse).
MINDIST =  1e-18


class Example:
    """
    An example : 
    vector = vector representation of an object (Ovector)
    gold_class = gold class for this object
    """
    def __init__(self, example_number, gold_class):
        self.gold_class = gold_class
        self.example_number = example_number
        self.vector = Ovector()

    def add_feat(self, featname, val):
        self.vector.add_feat(featname, val)


class Ovector:
    """
    Vector representation of an object to classify

    members
    - f= simple dictionnary from feature names to valuers
         Absent keys correspond to null values
    - norm_square : square value of the norm of this vector
    """
    def __init__(self):
        self.f = {}
        self.norm_square = 0 # to be filled later

    def add_feat(self, featname, val=0.0):
        self.f[featname] = val
        self.norm_square = self.norm_sq(self.f)


    def prettyprint(self):
        # sort features by decreasing values (-self.f[x])
        #           and by alphabetic order in case of equality
        for feat in sorted(self.f, key=lambda x: (-self.f[x], x)):
            print(feat+"\t"+str(self.f[feat]))

    def distance_to_vector(self, other_vector):
        """ Euclidian distance between self and other_vector, 
        Requires: that the .norm_square values be already computed """
        
        other_vector.norm_square = self.norm_sq(other_vector.f)
        dist = sqrt(self.norm_square + other_vector.norm_square - (2*self.dot_product(self.f, other_vector.f))) 
        return dist 
        
        # TODO
        # NB: use the calculation trick
        #   sigma [ (ai - bi)^2 ] = sigma (ai^2) + sigma (bi^2) -2 sigma (ai*bi) 
        #                         = norm_square(A) + norm_square(B) - 2 A.B

        #return 0
    
    def norm_sq (self, f1):
        
        return sum([val**2 for val in list(f1.values())])
    

    def dot_product(self, f1, other_vector):
        """ Returns dot product between self and other_vector """

        a1=list(f1.keys())
        a2=list(other_vector.keys())
        k=list(set(a1+a2))

        f_copy=dict(f1)

        
        for i in k:
            if i not in f_copy:
                f_copy[i]=0
            if i not in other_vector:
                other_vector[i]=0

        return sum([f_copy[i]*other_vector[i] for i in f_copy])

        
        
        """
        for val_1 in list(self.f.values()):
            for val_2 in list(other_vector.values()):
                dot_pdt = val_1 * val_2
        return dot_pdt 
        """
        
        # TODO
        #return 0

    def cosine(self, other_vector):
        """ Returns cosine of self and other_vector """
        
        return self.dot_product(self.f, other_vector.f)/(sqrt(self.norm_square)*sqrt(other_vector.norm_square))
        
        # TODO
        #return 0


class KNN(Ovector):
    """
    K-NN for document classification (multiclass classification)

    members = 

    K = the number of neighbors to consider for taking the majority vote

    examples = list of Example instances

    """
    def __init__(self, examples, K=5, weight_neighbors=None, use_cosine=False, trace=False):
        # examples = list of Example instances
        self.examples = examples
        # the number of neighbors to consider for taking the majority vote
        self.K = K
        # boolean : whether to weight neighbors (by inverse of distance) or not
        self.weight_neighbors = weight_neighbors

        # boolean : whether to use cosine similarity instead of euclidian distance
        self.use_cosine = use_cosine

        # whether to print some traces or not
        self.trace = trace
        

    def classify(self, ovector):
        """
        K-NN prediction for this ovector,
        for k values from 1 to self.K

        Returns: a K-long list of predicted classes,
        the class at position i is the K-NN prediction when using K=i
        """
        k_list=[]

        ##Get sorted distance list
        l=self.dist_calc(ovector)
        #print("L :",l)

        ##run a loop over K (select first k instances from the sorted list and get the majority)
        for i in range(1,self.K+1):
            class_vals=[j[1] for j in l[:i]]
            k_list.append(self.maj(class_vals))

        return k_list

    def dist_calc(self,ovector):

         l= [[ovector.distance_to_vector(i.vector),i.gold_class] for i in self.examples]
         l.sort()
         return l

    def maj(self, c):

        p=[[c.count(i), i] for i in set(c)]
        p.sort(key=lambda x: (-x[0],x[1]))
        return p[0][1]
        
        """
        d={}
        for i in set(c):
            d[i]=c.count(i)

        l=sorted(c, key=lambda x: (-c[x], x))
        return l[0]
        """
    
        #TODO

    def evaluate_on_test_set(self, test_examples):
        """ Runs the K-NN classifier on a list of Example instances
        and evaluates the obtained accuracy

        Returns: a K-long list of accuracies,
        the accuracy at position i is the one obtained when using K=i
        """
        acc=[0]*self.K
        #print(test_examples)

        ##Version 1
        for i in test_examples: 
            #print(i.vector)
            pred_classes = self.classify(i.vector)
            #print(pred_classes)

            for j in range(len(pred_classes)):
                if i.gold_class==pred_classes[j]:
                    acc[j]+=1
        #print(acc)
        
        return [a/len(test_examples) for a in acc]

       
        # TODO
        #return []
        
        

def read_examples(infile):
    """ Reads a .examples file and returns a list of Example instances """
    stream = open(infile)
    examples = []
    example = None
    while 1:
        line = stream.readline()
        if not line:
            break
        line = line[0:-1]
        if line.startswith("EXAMPLE_NB"):
            if example != None:
                examples.append(example)
            cols = line.split('\t')
            gold_class = cols[3]
            example_number = cols[1]
            example = Example(example_number, gold_class)
        elif line and example != None:
            (featname, val) = line.split('\t')
            example.add_feat(featname, float(val))

    
    if example != None:
        examples.append(example)
    return examples



usage = """ K-NN DOCUMENT CLASSIFIER

  """+sys.argv[0]+""" [options] TRAIN_FILE TEST_FILE

  TRAIN_FILE and TEST_FILE are in *.examples format

"""

parser = argparse.ArgumentParser(usage = usage)
parser.add_argument('train_file', default=None, help='Examples that will be used for the K-NN prediction (in .examples format)')
parser.add_argument('test_file', default=None, help='Test examples de test (in .examples format)')
parser.add_argument('-k', "--k", default=1, type=int, help='Hyperparameter K : maximum number of neighbors to consider (all values between 1 and k will be tested). Default=1')
parser.add_argument('-v', "--trace", action="store_true", help="Toggles the verbose mode. Default=False")
parser.add_argument('-w', "--weight_neighbors", action="store_true", help="If set, neighbors will be weighted before majority vote. If cosine: cosine weighting, if distance, weighting using the inverse of the distance. Default=False")
parser.add_argument('-c', "--use_cosine", action="store_true", help="Toggles the use of cosine similarity instead of euclidian distance. Default=False")
args = parser.parse_args()

#------------------------------------------------------------
# Loading training examples
training_examples = read_examples(args.train_file)
# Loading test examples
test_examples = read_examples(args.test_file)

myclassifier = KNN(examples = training_examples,
                   K = args.k,
                   weight_neighbors = args.weight_neighbors,
                   use_cosine = args.use_cosine,
                   trace=args.trace)

# classification and evaluation on test examples
accuracies = myclassifier.evaluate_on_test_set(test_examples)


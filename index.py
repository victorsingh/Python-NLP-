#Victor Singh NLP HW 2

class createModel:

  def __init__(self):
    self.trainingObject = {}
    # self.data = givenInformation
    self.parseDataSet()
    # print self.trainingObject, 'roger'
    self.generateCounts(self.trainingObject)

  def parseDataSet(self):
    x = open('movie-review.NB')
    # print x.readlines()
    for line in x.readlines():
      miniArr = line.split(' ')
      for commaWord in range(len(miniArr)):
        modMe = miniArr[commaWord].split(',')[0]
        modMe = modMe.split('\n')[0]
        miniArr[commaWord] = modMe
      # print miniArr
      self.generateDictionary(miniArr)
    #print self.trainingObject

  def generateDictionary(self, miniArr):
    # print miniArr
    label = miniArr[0]
    prior = miniArr[len(miniArr)-1]
    # print prior
    wordArray = miniArr[1:len(miniArr)-1]
    self.trainingObject[label] = {'data': wordArray, 'prior': prior}

  def generateCounts(self, data):
    #CANNOT COUNT REPEATED WORDS :)
    newDict = {}
    newDictUni = {}
    for sentenceIndex in data.values():
      # print sentenceIndex['data']
      arr = {}
      for word in sentenceIndex['data']:
        if newDict.has_key(word + '|' + sentenceIndex['prior']) and arr.has_key(word + '|' + sentenceIndex['prior']) is False:
          newDict[word + '|' + sentenceIndex['prior']] += 1
          arr[word + '|' + sentenceIndex['prior']] = True
        elif newDict.has_key(word) and arr.has_key(word) is True:
          continue
        else:
          newDict[word + '|' + sentenceIndex['prior']] = 1
          arr[word + '|' + sentenceIndex['prior']] = True
      self.wordCountGivenPrior = newDict


    for sentenceIndex in data.values():
      arrUni = {}
      for word in sentenceIndex['data']:
        if newDictUni.has_key(word) and arrUni.has_key(word) is False:
          newDictUni[word] += 1
          arrUni[word] = True
        elif newDictUni.has_key(word) and arrUni.has_key(word) is True:
          continue
        else:
          newDictUni[word] = 1
          arrUni[word] = True
    self.independentWordCount = newDictUni

    priorParameters = {}
    for sentenceIndex in data.values():
        if priorParameters.has_key(sentenceIndex['prior']):
          priorParameters[sentenceIndex['prior']] += 1
        else:
          priorParameters[sentenceIndex['prior']] = 1

    self.priorWords = priorParameters

  def setConditionalProbabilities(self):
   # go through independent word count, get conditionals, divide then by either action or comedy
    conditionalDict = {}
    for Ckey in self.wordCountGivenPrior:
      # print self.wordCountGivenPrior.get(Ckey)
      for Wkey in self.priorWords:
        # print Ckey.split('|')[1]
        if Ckey.split('|')[1] == Wkey:
          # print Ckey, str(self.wordCountGivenPrior.get(Ckey))+"/"+str(self.priorWords.get(Wkey))
          conditionalDict[Ckey] = float(self.wordCountGivenPrior.get(Ckey))/float(self.priorWords.get(Wkey))
          if conditionalDict[Ckey] > 1:
            conditionalDict[Ckey] = 1.0

    self.conditionalProbabilities = conditionalDict

  def getConditionalProbabilities(self):
    return self.conditionalProbabilities


  def classify(self, data):
    classifyThisData = data
    smoothQueue = []
    for key in classifyThisData:
      self.check4Zeros(key, smoothQueue)
    print '\n', smoothQueue , "these probabilites need to be smoothened since they are currently 0 in training data"

    for newWord in smoothQueue:
      getConditional = newWord.split('|')[1]
      self.wordCountGivenPrior[newWord] = 0
      for key in self.wordCountGivenPrior:
        if(key.split('|')[1] == getConditional):
          # print key, "will be incremented"
          self.wordCountGivenPrior[key] += 1

    self.setConditionalProbabilities()
    print '\n', self.getConditionalProbabilities(), 'These are out probabilities after smoothening'
    self.naiveBayes(data)


  def check4Zeros(self, givenWord, smoothQueue):
    addConditionals = []
    for key in self.priorWords:
      # print key, givenWord
      addConditionals.append(givenWord + '|' + key)

    for newConditionals in addConditionals:
      if self.wordCountGivenPrior.has_key(newConditionals) is False:
        smoothQueue.append(newConditionals)

      # if self.wordCountGivenPrior.has_key(newConditionals):
      #   print 'We have ', newConditionals, ' already'
      # else: # print 'We DONT have', newConditionals
      #   smoothQueue.append(newConditionals)

  def naiveBayes(self, data):
    probOfPriorParams = {}
    getPriorParamProbs = []
    classTotal = []
    totalPriors = 0
    # print self.priorWords
    for key in self.priorWords:
      totalPriors += self.priorWords[key]

    for key in self.priorWords:
      probOfPriorParams[key] = float(self.priorWords[key])/totalPriors

    desiredProbs = self.returnDocumentProbs(data)

    for ConditonalBlock in desiredProbs:
      arr = {}
      for isolatedConditional in ConditonalBlock:
        arr[isolatedConditional] = self.getConditionalProbabilities()[isolatedConditional]
      classTotal.append(arr)


    for key in probOfPriorParams:
      for ConditonalBlock in classTotal:
        for keyx in ConditonalBlock:
          # print keyx, 'keyx' , key
          if len(keyx.split('|'))>1:
            if keyx.split('|')[1] == key:
              ConditonalBlock[key] = probOfPriorParams[key]
            break

    for ConditonalBlock in classTotal:
      total = 1
      NewObject = {}
      DescriptionString = ''
      for prob in ConditonalBlock:
        if len(prob.split('|')) == 1:
          DescriptionString = prob
        total *= ConditonalBlock[prob]
      NewObject[DescriptionString] = total
      getPriorParamProbs.append(NewObject)

    print "\n", classTotal, 'These are the probabilities we used to calculate naive bayes'

    print "\n", getPriorParamProbs, 'These are the probabilities for each class'

    FinalResultForClass = ''
    finalresultProb = 0
    for classProbability in getPriorParamProbs:
      for prob in classProbability:
        if classProbability[prob] > finalresultProb:
          finalresultProb = classProbability[prob]
          FinalResultForClass = prob

    print "\n", 'The most likley class is', FinalResultForClass, 'with a result of', finalresultProb



  def returnDocumentProbs(self, data):
    isolateProbs = []
    for priorParams in self.priorWords:
      bigramArr = []
      for key in self.getConditionalProbabilities():
        # print key
        if key.split('|')[0] in data and key.split('|')[1] in priorParams:
          bigramArr.append(key)
      isolateProbs.append(bigramArr)

    # print isolateProbs

    return isolateProbs



print 'VICTOR SINGH HW 2 NLP'
myData = createModel()
myData.setConditionalProbabilities()
print "\n", myData.getConditionalProbabilities(), "These are the probabilities before adding the document"
# myData.generateCounts()

document = ['fast', 'couple', 'shoot', 'fly']

print '\n', document, 'this is the document we are passing in'

myData.classify(document)

# print myData.getConditionalProbabilities()






# print getCountsDict(training)

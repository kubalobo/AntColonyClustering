import pandas as pd
import numpy as np
import math
import os
import imageio

rng = np.random.default_rng()


class Ant:
    def __init__(self):
        self.x = rng.integers(0, boardSize)
        self.y = rng.integers(0, boardSize)
        self.isCarring = False
        self.carriedSeedId = -1


    def tick(self):
        if (self.isCarring):
            self.move()
        else:
            self.teleport()

        seedId = self.isStandingOnSeed()
        if seedId != -1:
            if not self.isCarring:
                self.pickUpTrial(seedId)
        else:
            if self.isCarring:
                self.dropTrial()

        pass


    def teleport(self):
        targetSeedId = rng.integers(0, len(data.index))
        self.x = data['x'][targetSeedId]
        self.y = data['y'][targetSeedId]


    def move(self):
        # TODO: Needs improvement - ant is generally constantly in the same region 
        deltaX = rng.integers(-1, 2)
        deltaY = rng.integers(-1, 2)

        newX = self.x + deltaX
        if(newX >= 0 and newX < boardSize):
            self.x = newX

        newY = self.y + deltaY
        if(newY >= 0 and newY < boardSize):
            self.y = newY
        pass


    def isStandingOnSeed(self):
        i = 0
        for x, y in zip(data['x'], data['y']):
            if (x == self.x) and (y == self.y):
                if (data['isOnTheGround'][i]):
                    return i
            i += 1
        return -1


    def scanEnvironment(self):
        closeSeeds = []

        i = 0
        for x, y in zip(data['x'], data['y']):
            if (x >= self.x - antScanDistance) and (x <= self.x + antScanDistance):
                if (y >= self.y - antScanDistance) and (y <= self.y + antScanDistance):
                    # distance = math.sqrt((x - self.x)  ** 2 + (y - self.y) ** 2)
                    # if (distance <= antScanDistance):
                    closeSeeds.append(i)
            i += 1

        return closeSeeds


    def calculateLocalSimilarity(self, id):
        closeSeeds = self.scanEnvironment()
        
        sum = 0
        for seed in closeSeeds:
            sum += 1 - (abs(data['value1'][seed] - data['value1'][id]) / dissimilarityScaleValue1)

        localSimilarity = sum / neighborhood
        if (localSimilarity < 0):
            localSimilarity = 0

        # print(localSimilarity)
        
        return localSimilarity

    # Propability
    def pickUpTrial(self, id):
        localSimilarity = self.calculateLocalSimilarity(id)

        propability = (gamma1 / (gamma1 + localSimilarity)) ** 2
        # print(propability)
        if(propability > rng.random()):
            self.pickUp(id)
        pass

    def pickUp(self, id):
        data['isOnTheGround'][id] = False
        self.isCarring = True
        self.carriedSeedId = id
        pass

    # Propability
    def dropTrial(self):
        localSimilarity = self.calculateLocalSimilarity(self.carriedSeedId)

        if(localSimilarity < gamma2):
            propability = localSimilarity
        else:
            propability = 1
        

        if(propability > rng.random()):
            self.drop()
        pass

    def drop(self):
        data['isOnTheGround'][self.carriedSeedId] = True
        data['x'][self.carriedSeedId] = self.x
        data['y'][self.carriedSeedId] = self.y

        self.isCarring = False
        self.carriedSeedId = -1
        pass


list_boardSize = [37]
list_numberOfAnts = [1]
list_antScanDistance = [1]
list_gamma1 = [0.1, 0.3, 0.5, 0.7, 0.9]
list_gamma2 = [0.1, 0.2, 0.3, 0.4, 0.5]
list_ticks = [100010]
# neighborhood = (2 * (antScanDistance ) + 1) ** 2



for boardSize in list_boardSize:
    for numberOfAnts in list_numberOfAnts:
        for antScanDistance in list_antScanDistance:
            for gamma1 in list_gamma1:
                for gamma2 in list_gamma2:
                    for ticks in list_ticks:
                        ticks = ticks / numberOfAnts
                        neighborhood = (2 * (antScanDistance ) + 1) ** 2
                        
                        data = pd.read_csv(
                            "./Audytorium/sdmt1.txt",
                            sep='\t',
                            header=None,
                            names=['depth', 'value1', 'value2']
                        )

                        data.insert(0, 'ID', range(0, 0 + len(data)))

                        spawnPositions = pd.DataFrame(rng.integers(0, boardSize, size=(len(data.index), 2)), columns=list('xy'))

                        data = pd.concat([data, spawnPositions], axis=1)

                        data.insert(6, 'isOnTheGround', True)

                        dissimilarityScaleValue1 = data['value1'].max() - data['value1'].min()

                        ants = []
                        for i in range(0, numberOfAnts):
                            ants.append(Ant())

                        folder = "b" + str(boardSize) + \
                                    "_a" + str(numberOfAnts) + \
                                    "_d" + str(antScanDistance) + \
                                    "_g" + str(gamma1) + \
                                    "_gg" + str(gamma2)
                                    # "ticks" + str(ticks)

                        print(folder)
                        if folder in os.listdir():
                            print('Already exist')
                            continue
                        os.mkdir(folder)

                        i = 0
                        for y in range(0, int(ticks)):
                            data['isOnTheGround'] = True
                            for ant in ants:
                                ant.tick()
                                if((i % 50000) == 0 and i != 0):
                                    ax = data.plot.scatter(x="x", y="y", xlim=(0, boardSize), ylim=(0, boardSize), s=30, c=data["value1"], cmap='viridis', alpha=0.5)
                                    ax.figure.savefig(folder + "/" + "" + str(i) + ".jpg")
                                i += 1

                        
                        # images = []
                        # for filename in os.listdir(folder):
                        #     images.append(imageio.imread(folder + '\\' + filename))
                        # imageio.mimsave('./' + folder + '.gif', images, fps=5)
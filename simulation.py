from queue import PriorityQueue, Queue
from numpy import random as rnd
from numpy import math

def createLogFunction(base):
    def customLog(number):
        return math.log(number, base)
    customLog.__name__ = f"logBase{int(base)}"
    return customLog
loge = createLogFunction(math.e)

class TelescopeModeling(object):
    WITH_PRIV = 0
    NO_PRIV = 1

    ARRIVAL_TIME_INDEX = 1
    PRIV_TYPE_INDEX = 0
    SERVE_TIME_INDEX = 2

    def _logThese(self, *params):
        if not self.logging:
            return
        for p in params:
            self.logFile.write(str(p) + '\t')
        self.logFile.write('\n')

    def _newFile(self, index):
        self.logFile = open(f'logs_{index}.txt', mode='w')
        self._logThese('currentTime, ' , 'priv ' , 'arrivedAt ' , 'servedTime ' , 'waitingTime ')
        
    def _printFirst10(self, l):
        for i in range(min(10, len(l))):
            print(l[i])

    def __init__(self, n, s, a):
        self.n = n
        self.s = s
        self.a = a
        self.logging = True

    def _getClientsQueue(self):
        # X = log(1 - U) / -lambda
        q = Queue()
        ldaArrival = 1 / self.a
        ldaServe = 1 / self.s
        arrivalTime = 0
        while arrivalTime <= 6*60:
            u = rnd.uniform()
            arrivalTime += loge(1 - u) / -ldaArrival
            u = rnd.uniform()
            serveTime = loge(1 - u) / -ldaServe
            q.put((arrivalTime, serveTime))
        return q

    def _getPrivilege(self, queueSize):
        if queueSize == 0:
            return self.NO_PRIV
        return rnd.randint(2)
        # return (self.NO_PRIV if queueSize == 0 else rnd.randint(2))

    def _getArrivedClients(self, clients, q, currentTime): # update q, take care of privellage
        while not clients.empty() and clients.queue[0][0] <= currentTime:
            priv = self._getPrivilege(len(q.queue))
            client =(priv, *clients.get())
            q.put(client)

    def _simulate(self):
        stats = {
            "priv_numUsers": 0,
            "noPriv_numUsers": 0,
            "priv_waitingTime": 0,
            "noPriv_waitingTime": 0,
        }
        # print(stats)

        clients = self._getClientsQueue() # future clients
        q = PriorityQueue() # presentClients (arrived clients sorted with priv first, secondly with arrival time)

        currentTime = 0 # start point
        client =(self._getPrivilege(len(q.queue)),*clients.get())
        q.put(client)
        currentTime = client[self.ARRIVAL_TIME_INDEX]
        while(not q.empty()): # empty clients and empty queues
            clientInService = q.get()

            # statistics
            self._logThese(currentTime , clientInService[self.PRIV_TYPE_INDEX] , clientInService[self.ARRIVAL_TIME_INDEX] , clientInService[self.SERVE_TIME_INDEX] , currentTime - clientInService[self.ARRIVAL_TIME_INDEX])
            prefix = "priv" if (clientInService[self.PRIV_TYPE_INDEX] == self.WITH_PRIV) else "noPriv"
            stats[f'{prefix}_numUsers'] += 1
            stats[f'{prefix}_waitingTime'] += currentTime - clientInService[self.ARRIVAL_TIME_INDEX]

            currentTime += clientInService[self.SERVE_TIME_INDEX]

            # if there is no one in the queue, and no one is served now, update the time with the first future client
            if (q.empty() and len(clients.queue) > 0 and currentTime < clients.queue[0][0]): # TODO: remove currentTime < clients.queue[0][0], redundant
                self._logThese("-------- [empty clients]: last client end his service before any one else coming -------", currentTime)
                currentTime = clients.queue[0][0]
            self._getArrivedClients(clients, q, currentTime) # TODO, rename this function to update present clients

        stats['priv_avgWaitingTime'] = stats['priv_waitingTime'] / stats['priv_numUsers']
        stats['noPriv_avgWaitingTime'] = stats['noPriv_waitingTime'] / stats['noPriv_numUsers']

        stats['avgWaitingTime'] = (stats['priv_waitingTime'] + stats['noPriv_waitingTime']) / (stats['priv_numUsers'] + stats['noPriv_numUsers'])
        stats['profitGain'] = stats['priv_numUsers'] * 30
        # print(stats['noPriv_numUsers'], stats['priv_numUsers'])
        return stats

    def simulate(self, logging = True):
        finalStats = {
            "avgWaitingTime": 0,
            "priv_avgWaitingTime": 0,
            "noPriv_avgWaitingTime": 0,
            "profitGain": 0
        }
        for replicaIndex in range(self.n):
            if (replicaIndex <= 10 and logging):
                self._newFile(replicaIndex)
            else:
                logging = False
            self.logging = logging
            stats = self._simulate()
            for key in finalStats.keys():
                finalStats[key] += stats[key] / n
        return finalStats

if __name__ == "__main__":
    # n, s, a = int(input("n= ")), float(input("s= ")), float(input("a= "))
    n = 1000
    s = 1.1
    a = 1.0
    simulation = TelescopeModeling(n, s, a)
    stats = simulation.simulate(logging=False)
    print("=============================  main stats  =============================")
    for key, value in stats.items():
        print(key, '=', value)

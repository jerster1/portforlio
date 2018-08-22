import hashlib, sys, json, random

def hashMe(msg=""):
    if type(msg)!=str:
        msg = json.dumps(msg,sort_keys=True)
    if sys.version_info.major == 2:
        return unicode(hashlib.sha256(msg).hexdigest(),'utf-8')
    else:
        return hashlib.sha256(str(msg).encode('utf-8')).hexdigest()

def checkBlockHash(block):
    # Raise an exception if the hash does not match the block contents
    expectedHash = hashMe( block['contents'] )
    if block['hash']!=expectedHash:
        raise Exception('Hash does not match contents of block %s'%
                        block['contents']['blockNumber'])
    return

def checkBlockValidity(block,parent,state):
    parentNumber = parent['contents']['blockNumber']
    parentHash = parent['hash']
    blockNumber = block['contents']['blockNumber']

    for txn in block['contents']['blockNumber']:
        if isValidTxn(txn,state):
            state = updateState(txn,state)
        else:
            raise Exception('invalid transaction in block %s: %s'%(blockNumber,txn))
    checkBlockHash(block)
    if blockNumber!=(parentNumber+1):
        raise Exception('Hash does not match contents of block %s'%blockNumber)
    if block['contents']['parentHash'] != parentHash:
        raise Exception('Parent hash not accurate at block %s'%blockNumber)

        return state

random.seed(0)

def makeTransaction(maxValue=3):
    sign = int(random.getrandbits(1))*2 - 1
    amount = random.randint(1,maxValue)
    alicePays = sign * amount
    bobPays = -1 * alicePays
    return {u'Alice':alicePays,u'bob':bobPays}


txnBuffer = [makeTransaction() for i in range(30)]

def updateState(txn,state):
    state = state.copy()
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

def isValidTxn(txn,state):
    if sum(txn.values()) is not 0:
        return False

    for key in txn.keys():
        if key in state.keys():
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False
    return True

state = {u'Alcie':5,u'Bob':5}

print(isValidTxn({u'Alice': -3, u'Bob': 3}, state)) #basic transation
print(isValidTxn({u'Alice': -4, u'Bob': 3}, state)) #but we cant create or destroy tokens
print(isValidTxn({u'Alice': -6, u'Bob': 6}, state)) #we can't overdraft either
print(isValidTxn({u'Alice': -4, u'Bob': 2,'lisa':2}, state)) #creating new ueser is valid
print(isValidTxn({u'Alice': -4, u'Bob': 3,'lisa':2}, state)) #but same rules apply


state = {u'Alice':50, u'Bob':50}  # Define the initial state
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber':0,u'parentHash':None,u'txnCount':1,u'txns':genesisBlockTxns}
genesisHash = hashMe( genesisBlockContents )
genesisBlock = {u'hash':genesisHash,u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)

chain = [genesisBlock]

def makeBlock(txns,chain):
    parentBlock = chain[-1]
    parentHash = parentBlock[u'hash']
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
    txnCount = len(txns)
    blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,
                     u'txnCount':len(txns),'txns':txns}
    blockHash = hashMe(blockContents)
    block = {u'hash':blockHash,u'contents':blockContents}

    return block

blockSizeLimit = 5
while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)
    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn,state)
        if validTxn:
            txnList.append(newTxn)
            state = updateState(newTxn,state)
        else:
            print("ignored transaction")
            sys.stdout.flush()
            continue

    myBlock = makeBlock(txnList,chain)
    chain.append(myBlock)


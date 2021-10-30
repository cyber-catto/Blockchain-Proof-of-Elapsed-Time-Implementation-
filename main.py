import hashlib
import json
from time import time
from time import sleep
import sqlite3 as sl
from ecdsa import SigningKey
import random

#Restricing the blocksize to 3
transactionCount=0

#storing the current leader node
leaderNode=""
leaderNodeName="Genesis Block : No Leader"
class Blockchain(object):

    #Maintaining a dictionary with key as UserIDs and their respective balance as value.
    dict_obj={}
    elapsedTime_dictobj={}
    global leaderNode

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.complete_transactions = []

        self.new_block(previous_hash="The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.", proof=100)

    # Create a new block listing key/value pairs of block information in a JSON object. Reset the list of pending transactions & append the newest block to the chain.

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'Creator Node':leaderNodeName,
        }
        self.pending_transactions = []
        self.complete_transactions = []
        self.chain.append(block)

        return block

    #Search the blockchain for the most recent block.
    @property
    def last_block(self):
 
        return self.chain[-1]

    # Add a transaction with relevant info to the 'blockpool' - list of pending tx's. 
    def new_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        
        self.pending_transactions.append(transaction)
        return self.last_block['index']+1
        
    # receive one block. Turn it into a string, turn that into Unicode (for hashing). Hash with SHA256 encryption, then translate the Unicode into a hexidecimal string.
    def hash(self, block):
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        return hex_hash
    
    #Validating the blockchain.
    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] == self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                return False
            previous_block = block
            block_index += 1

        return True

    def verifyTransaction(self,number):
        if(len(self.pending_transactions) < number):
            print(f"Total number of unverified transations are less than {number}. Verified all transactions")
            self.complete_transactions.extend(self.pending_transactions)
            self.pending_transactions = []
            return

        if(len(self.pending_transactions)>0 and len(self.pending_transactions) <= 5):
            for i in range(0,number):
                temp = self.pending_transactions[0]
                self.complete_transactions.append(temp)
                self.pending_transactions.remove(temp)
            print(f"Verified {number} transactions")

        if(number<=0):
            print("Invalid input")
            return


#After reading user's choice of action, this function redirects to appropriate functions.
def choice(choice):
    if choice==1:
        insertNode()
    elif choice==2:
        insertTransaction()
    elif choice==3:
        displayBlockChain()
    else :
        print("\nInvalid Input Choice\n.")

#To add a new User to the USER Database and also blockchain's dictionary{id,amount}
def insertNode():
    print("Enter UserId : ")
    userId=input()
    print("Enter Name : ")
    userName=input()
    print("Enter Balance Amount : ")
    userBal=input()

    #signing the key for node verification
    msg=(userName+userId).encode()
    private_key = SigningKey.generate() # uses NIST192p
    signature = private_key.sign(msg)
    public_key = private_key.verifying_key

    #validating the Node using public key
    if(validateNode(public_key, signature, userId, userName) is True):

        record=(userId,userName,userBal)
        sql_insertUser = """INSERT INTO USER (id, name, balance) VALUES(?,?,?)"""
        with con:
            con.execute(sql_insertUser,record)

        #insert userId and balance in Bloackchain's dictionary object
        blockchain.dict_obj[int(userId)]=float(userBal)
        blockchain.elapsedTime_dictobj[int(userId)]=0

        print("\nNew Node details added.\n")
    else:
        print("Invalid node\n")

def validateNode(public_key, signature, userId, userName):

    print("New Node is being validated before joining the other verified nodes...")
    #node verification
    msg=(userName+userId).encode()
    res = public_key.verify(signature, msg)
    print("Verified:", res )
    return res

#To create and insert a new transaction in the block.
def insertTransaction():

    #reading transaction details.
    print("Enter Sender UserID :")
    senderId=int(input())
    print("Enter Receiver UserID :")
    receiverId=int(input())
    print("Enter Transfer Amount :")
    amount=float(input())

    global transactionCount

    #checking if the sender and receiver are already registered user, else asking user to register that user first.
    if (senderId in blockchain.dict_obj) and (receiverId == 000) :
       
        #checking if the sender has enough balance amount for transaction
        if blockchain.dict_obj[senderId]>amount:

            t = blockchain.new_transaction(senderId,receiverId,amount)
            blockchain.dict_obj[senderId]=blockchain.dict_obj[senderId]-amount
            blockchain.dict_obj[receiverId]=blockchain.dict_obj[receiverId]+amount

            #updating the current balance amounts of sender and receiver.
            sql = ''' UPDATE USER SET balance=? WHERE id = ?'''
            cur = con.cursor()
            cur.execute(sql, (blockchain.dict_obj[senderId],senderId))

            sql = ''' UPDATE USER SET balance=? WHERE id = ?'''
            cur = con.cursor()
            cur.execute(sql, (blockchain.dict_obj[receiverId],receiverId))

            con.commit()

            print("\nSUCESSFULL TRANSACTION : New transaction registered.\n")

            transactionCount+=1

            if transactionCount==3 :
                print("The number of transaction has reached the maximum value (3), Creating a new Block...")
                createBlock()

        else:
            print("TRANSACTION FAILED : Insufficient balance at the sender.")
    else:
        if (senderId not in blockchain.dict_obj):
            print("Check if both Sender and Receiver are registered Users,else first insert them.")
        else :
            print("Check if the Receiver ID is matching Dexter's userID.")



#displays the complete block chain
def displayBlockChain():
    blockchain.verifyTransaction(1)
    print("Genesis block: ", blockchain.chain)

#creating a blockchain object
blockchain = Blockchain()

#Creating a Database to store the existing user details(ID, Name, BalanceAmount)
#New Users can also be inserted in this DB.
con = sl.connect('UserDB.db')
with con:
    con.execute("""
        CREATE TABLE USER (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            balance INTEGER
        );
    """)

#initially reading all the existing user records from the file and inserting them into USER Database.
#Entry : id_number, Name, existing_Amount
data=[]
f=open("/home/anjali/Desktop/BT/UserRecordsInput.txt","r")
sql = 'INSERT INTO USER (id, name, balance) values(?, ?, ?)'

for record in f:
    data.append(record.split(','))

with con:
    con.executemany(sql, data)

#storing the id and corresponding balance amount value in blockchain's dictionary
with con:
    data = con.execute("SELECT id,balance FROM USER")
    for row in data:
        blockchain.dict_obj[int(row[0])]=float(row[1])
        blockchain.elapsedTime_dictobj[int(row[0])]=float(row[1])

#to print the intial user entries.
print(blockchain.dict_obj)

#reads proof value and creates a new block.
def createBlock():
    
    global leaderNode
    global leaderNodeName
    print("\nCreating a new block by Process of Leader Selection using Elapsed Time : ")
    # generate random number scaled to number of seconds in 1min
    # (1*60) = 60

    minTime=61
    for node in blockchain.elapsedTime_dictobj:
    
        #change 60 here accordingly to change the time range.
        rtime = int(random.random()*60)

        hours   = int(rtime/3600)
        minutes = int((rtime - hours*3600)/60)
        seconds = rtime - hours*3600 - minutes*60
        
        time_string = '%02d:%02d:%02d' % (hours, minutes, seconds)
        blockchain.elapsedTime_dictobj[node]= time_string

        if minTime>rtime:
            minTime=rtime
            leaderNode=node

    print("\nDisplaying random times (in range of 1min) assigned to each node : ")
    print(blockchain.elapsedTime_dictobj)

    print("\nNodes sleeping (Time elapsing).....")
    sleep(float(minTime))

    connectn = sl.connect('UserDB.db')
    tempCursor=connectn.cursor()
    tempCursor.execute("SELECT name FROM USER WHERE id=?",(leaderNode,))
    leaderNodeName = str(tempCursor.fetchone()[0])
    print("\nSelected Leader = {} (ID : {})".format(leaderNodeName,leaderNode))

    global transactionCount

    #Leader Selection

    #if the number of transaction is less than 3, block is not created
    if transactionCount<3:
        print("\nInsufficient transactions to create a block (BlockSize taken (default) =3)\n")
    else:
        print("\nCreating a new block with....proof(Minimum Elapsed Time) ="+str(minTime))
        blockchain.new_block(minTime)
        transactionCount=0

        #when the news of the elected leader is broadcasted to all the remaining nodes their random time values can be reset
        for node in blockchain.elapsedTime_dictobj:
            blockchain.elapsedTime_dictobj[node]= 0

        print("\nAfter the news of the elected leader is broadcasted to all the remaining nodes their random time values are reset")
        print(blockchain.elapsedTime_dictobj)

#To read which action the user wants to perform and redirecting to corresponding functions.
loop=1
while(loop==1):
    print("\nEnter :\n1.Insert a new Node \n2.Enter a transaction.\n3.Display the BlockChain. \n4.Exit\n")
    c=int(input())
    if c==4:
        loop=0
    else:
        choice(c)
    

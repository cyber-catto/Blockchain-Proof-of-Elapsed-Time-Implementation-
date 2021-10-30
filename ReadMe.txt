Libraries and Installations needed:

random- for using random library to assign random time values for each node with in a given specified range
ecdsa (Elliptic Curve Digital Signature Algorithm) - to create public and private keys for validating the new nodes
sqlite3- for storing user details and modifying according to transactions 
time- for generating timestamps and random time and sleep function 



How to execute:
1. Execute the main file using 
python3 main.py

2. UserRecordsInput.txt contains the details of initial/ origial/ already verified users in the following fashion:
{User ID, User Name, User Balance}
Please change the address of the .txt file in line 239

3. UserDb.db must be deleted for a fresh execution

4. Change line number 271 to increase the range for elapsed time rate

5. Dexter will always be the receiver with intial balance=0

6. Use the switch case menu to perform the listed acitivies. 

7. The output of an acticity performed shall get displayed on the terminal. 

----------PoET Code Explanation---------------
A node  which wants to join the verified nodes has to be validated and it is done by creating private and public keys using the ECDSA library.

The node forwards this key when requesting to join the network. The nodes that are already a part of the network verify this key.

To select the leader of the nodes, or the node which creates the block which is linked to the existing blockchain, PoET algorithm initializes all the with a random time; the first one whose time expires becomes the winner. This means that it creates a new block. (Fairness of Algorithm is based on the randomness of the timers given to the nodes in this process.)

Later this news is broadcasted to the remaining nodes. (In our implementation, to indicate the receiving of this news, we have reset the random time values of all the nodes to zero.)





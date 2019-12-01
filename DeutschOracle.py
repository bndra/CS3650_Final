#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
# Importing standard Qiskit libraries and configuring account
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer, IBMQ
from qiskit.compiler import transpile, assemble
from qiskit.tools.jupyter import *
# Loading your IBM Q account(s)
IBMQ.load_accounts()
provider = IBMQ.get_provider(hub='ibm-q')
provider.backends()


# In[2]:


import qiskit as qk
#IBMQ.save_account('not publicly displaying my auth key')


# In[3]:


inputs = qk.QuantumRegister(2)
outputs = qk.ClassicalRegister(2)


# In[4]:


flipInput0 = qk.QuantumCircuit(inputs,outputs) #inputs[0] is by default = 0
flipInput0.x(inputs[0])                        #call this once at the start to flip it to 1

flipInput1 = qk.QuantumCircuit(inputs,outputs) #inputs[1] is default = 0
flipInput1.x(inputs[1])                        #one call at the start flips it to 1


# In[5]:


DeutschOracle = qk.QuantumCircuit(inputs,outputs) #preprocessing for quantum computation
DeutschOracle.x(inputs)                           #set to 1,1
DeutschOracle.h(inputs)                           #hadamard generates the correct superposition


# In[6]:


#the 4 unary operations
ID = qk.QuantumCircuit(inputs,outputs)  #identity operator on classical bits
ID.cx(inputs[0],inputs[1])              #implemented through a cnot gate. 

Not = qk.QuantumCircuit(inputs,outputs) #negation operator on classical bits
Not.cx(inputs[0],inputs[1])             #same as identity but...
Not.x(inputs[1])                        #the output is flipped by an x gate

Const0 = qk.QuantumCircuit(inputs,outputs) #set to zero operator on classical bits

Const1 = qk.QuantumCircuit(inputs,outputs) #set to one operator on classical bits
Const1.x(inputs[1])                        #output bit is set to one by an x gate (default is 0)


# In[7]:


Zmeasure = qk.QuantumCircuit(inputs,outputs) #simply read the values of the qubits
Zmeasure.measure(inputs,outputs)             #useful for evaluating eigenvector states (0 or 1)


# In[8]:


Xmeasure = qk.QuantumCircuit(inputs,outputs) #interpret superposition states
Xmeasure.h(inputs)                           #by collapsing them with a hadamard
Xmeasure.measure(inputs,outputs)


# In[9]:


#eigenvector tests. proof that our 4 unary operators are what they say they are for cbits.
#note how we require two queries to verify each operator,
#even just to tell if it's constant or variable
testID0 = ID + Zmeasure               #test ID op on 0
testID1 = flipInput0 + ID + Zmeasure  #test ID op on 1

testNot0 = Not + Zmeasure             #test Not op on 0
testNot1 = flipInput0 + Not + Zmeasure #test Not op on 1

testConst0_0 = Const0 + Zmeasure      #test const0 on 0
testConst0_1 = flipInput0 + Const0 + Zmeasure #"    " 1

testConst1_0 = Const1 + Zmeasure      #test const1 on 0
testConst1_1 = flipInput0 + Const1 + Zmeasure #"    " 1
#for any one of our four unary operators, f(x)
#we recieve outputs[2]
#where outputs[0] = inputs[0]
#and   outputs[1] = f(outputs[0])

# In[10]:

#using a quantum simulator provided by IBM
job = qk.execute([testID0,testID1,testNot0,testNot1,testConst0_0,testConst0_1,testConst1_0,testConst1_1],backend=provider.get_backend('ibmq_qasm_simulator'),shots=1)


# In[11]:


job.result().get_counts(testID0) #output is of this format: {'outputbit inputbit': numberofoccurences}
#which means we should see {'00':1}
job.result().get_counts(testID1) 
#should see {'11':1}
#the output bit changes based on the input bit, we can see in 2 queries that this is variable

# In[13]:


job.result().get_counts(testNot0) 
# {'10':1}
job.result().get_counts(testNot1) 
#{'01':1}
#output depends on input, 2 queries to verify variable

# In[15]:


job.result().get_counts(testConst0_0) 
#{'00':1}
job.result().get_counts(testConst0_1) 
#{'01':1}
#output stays 0 regardless of input, function is constant

# In[17]:


job.result().get_counts(testConst1_0)
#{'10':1}
job.result().get_counts(testConst1_1)
#{'11':1}
#output is 1 regardless of input, constant

# In[19]:


#Superposition tests. Can we tell the difference between const and variable operators in a single query??
testID = DeutschOracle + ID + Xmeasure          #difference between these and the classical bits:
testNot = DeutschOracle + Not + Xmeasure        #set bits to 1 and hadamard before and hadamard after the function then measure.
testConst0 = DeutschOracle + Const0 + Xmeasure
testConst1 = DeutschOracle + Const1 + Xmeasure
#output format is slightly different for these. 
#the second bit is the important one to look at
#if it's 0, the function is variable, if 1 the function is constant
#first bit should always be 1, but sometimes there are errors reading the qbits
#10 for variable functions: ID, NOT 
#11 for const functions : Const0, Const1

# In[20]:

#using one of IBM's actual quantum computers: ibmqx2
quantumJob = qk.execute([testID,testNot,testConst0,testConst1],backend=provider.get_backend('ibmqx2'),shots=300) 

# In[21]:


quantumJob.result().get_counts(testID)#ID is a variable function so we should see a second bit of 0
#{'00': 8, '01': 22, '11': 80, '10': 190} getting 10 the most often by far, consistent


# In[22]:


quantumJob.result().get_counts(testNot)#Not is also variable, should see 0 as well
#{'00': 12, '01': 24, '11': 82, '10': 182} getting 10 most often again, consistent

# In[23]:


quantumJob.result().get_counts(testConst0)
#{'01': 14, '11': 282, '10': 4} getting 11 most often, good

# In[24]:


quantumJob.result().get_counts(testConst1)
#{'01': 10, '11': 283, '10': 7} getting 11 most often, good



# imagine if these four unary operators were black boxes and we wanted to identify which were constant/variable
# that's essentially the Deutsch Oracle question, and we've shown here that it takes 2 queries to answer it 
# using classical bits, and only a single query with qbits.
# why this happens is a bit difficult to answer, but I can say for certain that our unary operators here
# have drastically different effects on bits in superposition than they do on eigenvectors, at that it's 
# possible to use this to infer relationships between the bits rather than their exact values.





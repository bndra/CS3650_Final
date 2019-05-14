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


# In[2]:


import qiskit as qk
#IBMQ.save_account('auth key goes here')


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
#which means whatever numbers you see, apply the operator to the lsb to obtain the msb


# In[10]:


job = qk.execute([testID0,testID1,testNot0,testNot1,testConst0_0,testConst0_1,testConst1_0,testConst1_1],backend=IBMQ.get_backend('ibmq_qasm_simulator',hub=None),shots=1)


# In[11]:


job.result().get_counts(testID0)


# In[12]:


job.result().get_counts(testID1)


# In[13]:


job.result().get_counts(testNot0)


# In[14]:


job.result().get_counts(testNot1)


# In[15]:


job.result().get_counts(testConst0_0)


# In[16]:


job.result().get_counts(testConst0_1)


# In[17]:


job.result().get_counts(testConst1_0)


# In[18]:


job.result().get_counts(testConst1_1)


# In[19]:


#Superposition tests. Can we tell the difference between const and variable operators in a single query??
testID = DeutschOracle + ID + Xmeasure
testNot = DeutschOracle + Not + Xmeasure
testConst0 = DeutschOracle + Const0 + Xmeasure
testConst1 = DeutschOracle + Const1 + Xmeasure
#outputs[0] = 0 indicates a variable operator
#outputs[0] = 1 indicates a const operator


# In[20]:


quantumJob = qk.execute([testID,testNot,testConst0,testConst1],backend=IBMQ.get_backend('ibmqx2',hub=None),shots=300)


# In[21]:


quantumJob.result().get_counts(testID)


# In[22]:


quantumJob.result().get_counts(testNot)


# In[23]:


quantumJob.result().get_counts(testConst0)


# In[24]:


quantumJob.result().get_counts(testConst1)


# In[ ]:





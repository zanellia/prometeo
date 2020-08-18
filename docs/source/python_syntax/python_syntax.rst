Python syntax
=============

prometeo is an embedded domain specific language based on Python. Hence, its 
syntax is based on Python. Below you find details regarding the most common 
supported Python constructs that prometeo is able to transpile to C.

variable declaration
--------------------

A variable can be declared as follows

.. code-block:: python

    <var_name> (id) : int = 1

Notice that, unlike in Python, type hints are strictly mandatory as they will instruct
prometeo's parser regarding the type of the variables being defined.

`if` statement
------------

An `if` statement takes the form 


.. code-block:: python

    if <cond>:
        ...


for loop
------------

A for loop takes the form 


.. code-block:: python

    for i in range([<start> (num, id)], <end> (num, id)):
        ...

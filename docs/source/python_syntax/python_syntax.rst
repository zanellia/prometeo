Python syntax
=============

prometeo is an embedded domain specific language based on Python. Hence, its 
syntax is based on Python. Below you find details regarding the most common 
supported Python constructs that prometeo is able to transpile to C.

variable declaration
--------------------

A variable can be declared as follows

.. code-block:: python

    <var_name> : <type> = <value> 

where `<var_name>` must be a valid identifier `<type>` must be a valid 
prometeo built-in type or a user-defined type and `<value>` must be 
an valid expression of type `<type>`. 

Example:

.. code-block:: python

    a : int = 1 

Notice that, unlike in Python, type hints are strictly mandatory as they will instruct
prometeo's parser regarding the type of the variables being defined.

`if` statement
------------

An `if` statement takes the form 


.. code-block:: python

    if <cond>:
        ...


`for` loop
------------

A `for` loop takes the form 


.. code-block:: python

    for i in range([<start>], <end>) 
        ...

where the optional parameter `<start>` must be an expression of type `int` (default value 0) and defines the starting value of the loop's index and  `<end>` must be an expression of type `<int>` which defines its final value. 

function definition
-------------------

Functions can be defined as follows


.. code-block:: python

    def <function_name> (<arg1> :  <arg_1_type>, ...) -> <ret_type> :

        ...

        return <ret_value>
        


class definition
----------------

prometeo supports basic classes of the following form

.. code-block:: python3 

    class <name>:
        def __init__(self, <arg1> : <arg_1_type>, ...) -> None:
            self.<attribute> : <type> = <value>
            ...

        def <method_name> (self,  <arg1> : <arg_1_type>, ...) -> <ret_type>: 
            ...

            return <ret_value>

main function
-------------

For consistency all main functions need to be defined as follows


.. code-block:: python 

    def main() -> int:

        ...

    return 0

pure Python blocks
-------------------

In order to be able to use the full potential of the Python language and 
its vast pool of libraries, it is possible to write *pure Python* blocks 
that are run only when prometeo code is executed directly from the Python intepreter (when --cgen is set to false). In particular, any line that is enclosed within `# pure >` and `# pure <` will be run only by the Python interpreter, but completely discarded by prometeo's parser. 


.. code-block:: python 

    # some prometeo code
    A : pmat = pmat(n,n)
    ...
    
    # pure >
    
    # this is only run by the Python interpreter (--cgen=False) 
    # and will not be transpiled)

    # some Python code 

    import numpy as np

    M = np.array([[1.0, 2.0],[0.0, 0.5]])
    print(np.linalg.eigvals(M))
    ...

    # pure <

    # some more prometeo code
    for i in range(n):
        for j in range(n):
            A[i, j] = 1.0
    ...
    

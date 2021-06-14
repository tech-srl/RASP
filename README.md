# RASP 

## Setup
#### Mac or Linux
Run `./setup.sh` . It will create a python3 virtual environment and install the dependencies for RASP. It will also try to install graphviz (the non-python part) and rlwrap on your machine. If these fail, you will still be able to use RASP, however: the interface will not be as nice without `rlwrap`, and drawing s-op computation flows will not be possible without `graphviz`. 
After having set up, you can run `./rasp.sh` to start the RASP read-evaluate-print-loop. 
#### Windows
Follow the instructions given in `windows instructions.txt`

## The REPL
After having set up, if you are in mac/linux, you can run `./rasp.sh` to start the RASP REPL. Otherwise, run `python3 RASP_support/REPL.py`
Use Ctrl+C to quit a partially entered command, and Ctrl+D to exit the REPL.

#### Initial Environment
RASP starts with the base s-ops: `tokens`, `indices`, and `length`. It also has the base functions `select`, `aggregate`, and `selector_width` as described in the paper, a selector `full_s` created through `select(1,1,==)` that creates a "full" attention pattern, and several other library functions (check out `RASP_support/rasplib.rasp` to see them). 

Additionally, the REPL begins with a base example, `"hello"`, on which it shows the output for each created s-op or selector. This example can be changed, and toggled on and off, through commands to the REPL.

All RASP commands end with a semicolon. Commands to the REPL -- such as changing the base example -- do not.

Start by following along with the examples -- they are kept at the bottom of this readme.

#### Note on input types:
RASP expects inputs in four forms: strings, integers, floats, or booleans, handled respectively by `tokens_str`, `tokens_int`, `tokens_float`, and `tokens_bool`. Initially, RASP loads with `tokens` set to `tokens_str`, this can be changed by assignment, e.g.: `tokens=tokens_int;`. When changing the input type, you will also want to change the base example, e.g.: `set example [0,1,2]`. 

Note that assignments do not retroactively change the computation trees of existing s-ops!


## Writing and Loading RASP files

To keep and load RASP code from files, save them with `.rasp` as the extension, and use the 'load' command without the extension. For example, you can load the examples file `paper_examples.rasp` in this repository to the REPL as follows:
```
>> load "paper_examples";
```
This will make (almost) all values in the file available in the loading environment (whether the REPL, or a different `.rasp` file): values whose names begin with an underscore remain private to the file they are written in.
Loading files in the REPL will also print a list of all loaded values.

#### Syntax Highlighting
For the Sublime Text editor, you can get syntax highlighting for `.rasp` files as follows:
1. Install package control for sublime (you might already have it: look in the menu [Sublime Text]->[Preferences] and see if it's there. If not, follow the instructions at https://packagecontrol.io/installation).
2. Install the 'packagedev' package through package control ([Sublime Text]->[Preferences]->[Package Control], then type [install package], then [packagedev])
3. After installing PackageDev, create a new syntax definition file through [Tools]->[Packages]->[Package Development]->[New Syntax Definition].
4. Copy the contents of `RASP_support/RASP.sublime-syntax` into the new syntax definition file, and save it as `RASP.sublime-syntax`.

[Above is basically following the instructions in http://ilkinulas.github.io/programming/2016/02/05/sublime-text-syntax-highlighting.html , and then copying in the contents of the provided `RASP.sublime-syntax` file]


## Examples

Play around in the REPL!  

Try simple elementwise manipulations of s-ops:
```
>> 3xindices =3 * indices;
   s-op: 3xindices
	 Example: 3xindices("hello") = [0, 3, 6, 9, 12]
>> indices+indices;
   s-op: out
	 Example: out("hello") = [0, 2, 4, 6, 8]
```

Change the base example, and create a selector that focuses each position on all positions before it:
```
>> set example "hey"
>> prevs=select(indices,indices,<);
    selector: prevs
 	 Example: prevs("hey") = 
			{0: [0, 0, 0], 1: [1, 0, 0], 2: [1, 1, 0]}
```

Check the output of an s-op on your new base example:
```
>> 3xindices;
   s-op: 3xindices
	 Example: 3xindices("hey") = [0, 3, 6]
```

Or on specific inputs:
```
>> 3xindices(["hi","there"]);
	 =  [0, 3]
>> 3xindices("hiya");
	= [0, 3, 6, 9]
```

Aggregate with the full selection pattern to compute the proportion of a letter in your input:
```
>> full_s;
    selector: full_s
    Example: full_s("hey") = 
      {0: [1, 1, 1], 1: [1, 1, 1], 2: [1, 1, 1]}
>> my_frac=aggregate(full_s,indicator(tokens=="e"));
    s-op: my_frac
 		Example: my_frac("hey") = [0.333]*3
```
Note: when an s-op's output is identical in all positions, RASP simply prints the output of one position, followed by  "` * X`" (where X is the sequence length) to mark the repetition.


Check if a letter is in your input at all:
```
>> "e" in tokens;
    s-op: out
   Example: out("hey") = [T]*3
```

Alternately, in an elementwise fashion, check if each of your input tokens belongs to some group:
```
>> vowels = ["a","e","i","o","u"];
    list: vowels = ['a', 'e', 'i', 'o', 'u']
>> tokens in vowels;
    s-op: out
   Example: out("hey") = [F, T, F]
```

Draw the computation flow for an s-op you have created, on an input of your choice:
(this will create a pdf in a subfolder `comp_flows` of the current directory)
```
>> draw(my_frac,"abcdeeee");
   =  [0.5]*8
```

Or simply on the base example:
```
>> draw(my_frac);
	=  [0.333]*3	 
```

If they bother you, turn the examples off, and bring them back when you need them:
```
>> examples off
>> indices;
    s-op: indices
>> full_s;
    selector: full_s
>> examples on
>> indices;
    s-op: indices
 	 Example: indices("hello") = [0, 1, 2, 3, 4]
```
You can also do this selectively, turning only selector or s-op examples on and off, e.g.: `selector examples off`.

Create a selector that focuses each position on all other positions containing the same token. But first, set the base example to `"hello"` for a better idea of what's happening:
```
>> set example "hello"
>> same_token=select(tokens,tokens,==);
    selector: same_token
   Example: same_token("hello") = 
      {0: [1, 0, 0, 0, 0],
       1: [0, 1, 0, 0, 0],
       2: [0, 0, 1, 1, 0],
       3: [0, 0, 1, 1, 0],
       4: [0, 0, 0, 0, 1]}
```

Then, use `selector_width` to compute, for each position, how many other positions the selector `same_token` focuses it on. This effectively computes an in-place histogram over the input:
```
>> histogram=selector_width(same_token);
    s-op: histogram
   Example: histogram("hello") = [1, 1, 2, 2, 1]
```

For more complicated examples, check out `paper_examples.rasp`!


# Experiments on Transformers
The transformers in the paper were trained, and their attention heatmaps visualised, using the code in this repository: https://github.com/tech-srl/RASP-exps


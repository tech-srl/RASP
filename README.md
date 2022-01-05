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
If you use the Sublime Text Editor, you can get RASP syntax highlighting by using the provided syntax file and instructions in the syntax_highlighting folder of this repository. 

If you use Emacs, you can get syntax highlighting, auto-indentation, and other cool features through Arthur Amalvy's Emacs major mode, which Arthur hosts (along with installation instructions) at https://gitlab.com/Aethor/rasp-mode .

## Examples

Play around in the REPL!  

Try simple elementwise manipulations of s-ops:
```
>>  threexindices =3 * indices;
     s-op: threexindices
 	 Example: threexindices("hello") = [0, 3, 6, 9, 12] (ints)
>> indices+indices;
     s-op: out
 	 Example: out("hello") = [0, 2, 4, 6, 8] (ints)
```
Change the base example, and create a selector that focuses each position on all positions before it:
```
>> set example "hey"
>> prevs=select(indices,indices,<);
     selector: prevs
 	 Example:
 			     h e y
 			 h |      
 			 e | 1    
 			 y | 1 1  
```

Check the output of an s-op on your new base example:
```
>> threexindices;
     s-op: threexindices
 	 Example: threexindices("hey") = [0, 3, 6] (ints)
```

Or on specific inputs:
```
>> threexindices(["hi","there"]);
	 =  [0, 3] (ints)
>> threexindices("hiya");
	 =  [0, 3, 6, 9] (ints)
```

Aggregate with the full selection pattern (loaded automatically with the REPL) to compute the proportion of a letter in your input:
```
>> full_s;
     selector: full_s
 	 Example:
 			     h e y
 			 h | 1 1 1
 			 e | 1 1 1
 			 y | 1 1 1
>> my_frac=aggregate(full_s,indicator(tokens=="e"));
     s-op: my_frac
 	 Example: my_frac("hey") = [0.333]*3 (floats)
```
Note: when an s-op's output is identical in all positions, RASP simply prints the output of one position, followed by  "` * X`" (where X is the sequence length) to mark the repetition.


Check if a letter is in your input at all:
```
>> "e" in tokens;
     s-op: out
 	 Example: out("hey") = [T]*3 (bools)
```

Alternately, in an elementwise fashion, check if each of your input tokens belongs to some group:
```
>> vowels = ["a","e","i","o","u"];
     list: vowels = ['a', 'e', 'i', 'o', 'u']
>> tokens in vowels;
     s-op: out
 	 Example: out("hey") = [F, T, F] (bools)
```

Draw the computation flow for an s-op you have created, on an input of your choice:
(this will create a pdf in a subfolder `comp_flows` of the current directory)
```
>> draw(my_frac,"abcdeeee");
	 =  [0.5]*8 (floats)
```

Or simply on the base example:
```
>> draw(my_frac);
	 =  [0.333]*3 (floats)
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
 	 Example: indices("hey") = [0, 1, 2] (ints)
```
You can also do this selectively, turning only selector or s-op examples on and off, e.g.: `selector examples off`.

Create a selector that focuses each position on all other positions containing the same token. But first, set the base example to `"hello"` for a better idea of what's happening:
```
>> set example "hello"
>> same_token=select(tokens,tokens,==);
     selector: same_token
 	 Example:
 			     h e l l o
 			 h | 1        
 			 e |   1      
 			 l |     1 1  
 			 l |     1 1  
 			 o |         1
```

Then, use `selector_width` to compute, for each position, how many other positions the selector `same_token` focuses it on. This effectively computes an in-place histogram over the input:
```
>> histogram=selector_width(same_token);
     s-op: histogram
 	 Example: histogram("hello") = [1, 1, 2, 2, 1] (ints)
```

For more complicated examples, check out `paper_examples.rasp`!


# Experiments on Transformers
The transformers in the paper were trained, and their attention heatmaps visualised, using the code in this repository: https://github.com/tech-srl/RASP-exps

# Citation
This repo is an implementation of RASP as presented in the paper "Thinking Like Transformers" (https://arxiv.org/abs/2106.06981). You can cite it using:
```
@InProceedings{pmlr-v139-weiss21a,
  title = 	 {Thinking Like Transformers},
  author =       {Weiss, Gail and Goldberg, Yoav and Yahav, Eran},
  booktitle = 	 {Proceedings of the 38th International Conference on Machine Learning},
  pages = 	 {11080--11090},
  year = 	 {2021},
  editor = 	 {Meila, Marina and Zhang, Tong},
  volume = 	 {139},
  series = 	 {Proceedings of Machine Learning Research},
  month = 	 {18--24 Jul},
  publisher =    {PMLR},
  pdf = 	 {http://proceedings.mlr.press/v139/weiss21a/weiss21a.pdf},
  url = 	 {http://proceedings.mlr.press/v139/weiss21a.html}
  }
```

from antlr4 import CommonTokenStream, InputStream
from collections.abc import Iterable

from zzantlr.RASPLexer import RASPLexer
from zzantlr.RASPParser import RASPParser
from zzantlr.RASPVisitor import RASPVisitor

from Environment import Environment, UndefinedVariable, ReservedName
from FunctionalSupport import UnfinishedSequence, UnfinishedSelect, Unfinished
from Evaluator import Evaluator, NamedVal, NamedValList, JustVal, \
				RASPFunction, ArgsError, RASPTypeError, RASPValueError
from Support import Select, Sequence, lazy_type_check

encoder_name = "s-op"

class ResultToPrint:
	def __init__(self,res,to_print):
		self.res, self.print = res, to_print

class LazyPrint:
	def __init__(self,*a,**kw):
		self.a, self.kw = a, kw
	def print(self):
		print(*self.a,**self.kw)

class StopException(Exception):
	def __init__(self):
		super().__init__()

debug = False

def debprint(*a,**kw):
	if debug:
		print(*a,**kw)

class ReturnExample:
	def __init__(self,subset):
		self.subset = subset

class LoadError(Exception):
	def __init__(self,msg):
		super().__init__(msg)

def is_comment(line):
	if not isinstance(line,str):
		return False
	return line.strip().startswith("#")

def formatstr(res):
	if isinstance(res,str):
		return "\""+res+"\""
	return str(res)

class REPL:
	def __init__(self):
		self.env = Environment(name="console")
		self.sequence_running_example = "hello"
		self.selector_running_example = "hello"
		self.sequence_prints_verbose = False
		self.show_sequence_examples = True
		self.show_selector_examples = True
		self.results_to_print = []
		self.print_welcome()
		self.load_base_libraries_and_make_base_env()

	def load_base_libraries_and_make_base_env(self):
		self.silent = True
		self.base_env = self.env.snapshot() # base env: the env from which every load begins
		# bootstrap base_env with current (basically empty except indices etc) env, then load
		# the base libraries to build the actual base env
		for l in ["RASP_support/rasplib"]:			
			self.run_given_line("load \""+l+"\";")
			self.base_env = self.env.snapshot()
		self.silent = False


	def set_running_example(self,example,which="both"):
		if which in ["both",encoder_name]:
			self.sequence_running_example = example
		if which in ["both","selector"]:
			self.selector_running_example = example

	def print_welcome(self):
		print("RASP 0.0")
		print("running example is:",self.sequence_running_example)

	def print_just_val(self,justval):
		val = justval.val
		if None is val:
			return
		if isinstance(val,Select):
			print("\t = ")
			print_select(val.created_from_input,val)
		elif isinstance(val,Sequence) and self.sequence_prints_verbose:
			print("\t = ",end="")
			print_seq(val.created_from_input,val,still_on_prev_line=True)
		else:
			print("\t = ",str(val).replace("\n","\n\t\t\t"))

	def print_named_val(self,name,val,ntabs=0,extra_first_pref=""):
		pref="\t"*ntabs
		if (None is name) and isinstance(val,Unfinished):
			name = val.name
		if isinstance(val,UnfinishedSequence):
			print(pref,extra_first_pref,"   "+encoder_name+":",name)
			if self.show_sequence_examples:
				if self.sequence_prints_verbose:
					print(pref,"\t Example:",end="")
					optional_exampledesc = name+"("+formatstr(self.sequence_running_example)+") ="
					print_seq(self.selector_running_example,val(self.sequence_running_example),still_on_prev_line=True,
										extra_pref=pref,lastpref_if_shortprint=optional_exampledesc)
				else:
					print(pref,"\t Example:",name+"("+formatstr(self.sequence_running_example)+\
						") =",val(self.sequence_running_example))
		elif isinstance(val,UnfinishedSelect):
			print(pref,extra_first_pref,"   selector:",name)
			if self.show_selector_examples:
				print(pref,"\t Example:")#,name+"("+formatstr(self.selector_running_example)+") =")
				print_select(self.selector_running_example,val(self.selector_running_example),extra_pref=pref)
		elif isinstance(val,RASPFunction):
			print(pref,extra_first_pref,"   "+str(val))
		elif isinstance(val,list):
			named = "   list: "+((name+" = ") if not None is name else "")
			print(pref,extra_first_pref,named,end="")
			flat = True not in [isinstance(v,list) or isinstance(v,dict) or isinstance(v,Unfinished) for v in val]
			if flat:
				print(val)
			else:
				print(pref,"[")
				for v in val:
					self.print_named_val(None,v,ntabs=ntabs+2)
				print(pref," "*len(named),"]")
		elif isinstance(val,dict):
			named = "   dict: "+((name+" = ") if not None is name else "")
			print(pref,extra_first_pref,named,end="")
			flat = True not in [isinstance(val[v],list) or isinstance(val[v],dict) or isinstance(val[v],Unfinished) for v in val]
			if flat:
				print(val)
			else:
				print(pref,"{")
				for v in val:
					self.print_named_val(None,val[v],ntabs=ntabs+3,extra_first_pref=formatstr(v)+" : ")
				print(pref," "*len(named),"}")

		else:
			print(pref,"   value:",((name+" = ") if not None is name else ""),formatstr(val))

	def print_example(self,nres):
		if nres.subset in ["both",encoder_name]:
			print("\t"+encoder_name+" example:",formatstr(self.sequence_running_example))
		if nres.subset in ["both","selector"]:
			print("\tselector example:",formatstr(self.selector_running_example))

	def print_result(self,rp):
		if self.silent:
			return
		if isinstance(rp,LazyPrint):
			return rp.print()
		if isinstance(rp,list): # a list of multiple ResultToPrint s -- probably the result of a multi-assignment
			for v in rp:
				self.print_result(v) 
			return
		if not rp.print:
			return
		res = rp.res
		if isinstance(res,NamedVal):
			self.print_named_val(res.name,res.val)
		elif isinstance(res,ReturnExample):
			self.print_example(res)
		elif isinstance(res,JustVal):
			self.print_just_val(res)

	def evaluate_replstatement(self,ast):
		if ast.setExample():
			return ResultToPrint(self.setExample(ast.setExample()), False)
		if ast.showExample():
			return ResultToPrint(self.showExample(ast.showExample()), True)
		if ast.toggleExample():
			return ResultToPrint(self.toggleExample(ast.toggleExample()), False)
		if ast.toggleSeqVerbose():
			return ResultToPrint(self.toggleSeqVerbose(ast.toggleSeqVerbose()), False)
		if ast.exit():
			raise StopException()

	def toggleSeqVerbose(self,ast):
		switch = ast.switch.text
		self.sequence_prints_verbose = switch == "on"

	def toggleExample(self,ast):
		subset = ast.subset
		subset = "both" if not subset else subset.text
		switch = ast.switch.text
		examples_on = switch=="on"
		if subset in ["both",encoder_name]:
			self.show_sequence_examples = examples_on
		if subset in ["both","selector"]:
			self.show_selector_examples = examples_on

	def showExample(self,ast):
		subset = ast.subset
		subset = "both" if not subset else subset.text
		return ReturnExample(subset)

	def setExample(self,ast):
		example = Evaluator(self.env,self).evaluateExpr(ast.example)
		if not isinstance(example,Iterable):
			raise RASPTypeError("example not iterable: "+str(example))
		subset = ast.subset
		subset = "both" if not subset else subset.text
		self.set_running_example(example,subset)
		return ReturnExample(subset)

	def loadFile(self,ast,calling_env=None):
		if None is calling_env:
			calling_env = self.env
		libname = ast.filename.text[1:-1]
		filename = libname + ".rasp"
		try:
			with open(filename,"r") as f:
				prev_example_settings = self.show_sequence_examples, self.show_selector_examples
				self.show_sequence_examples, self.show_selector_examples = False, False
				self.run(fromfile=f,env = Environment(name=libname,parent_env=self.base_env,stealing_env=calling_env),store_prints=True)
				self.filter_and_dump_prints() 
				self.show_sequence_examples, self.show_selector_examples = prev_example_settings
		except FileNotFoundError:
			raise LoadError("could not find file: "+filename)

	def get_tree(self,fromfile=None):
		try:
			return LineReader(fromfile=fromfile).get_input_tree()
		except AntlrException as e:
			print("\t!! antlr exception:",e.msg,"\t-- ignoring input")
		return None

	def run_given_line(self,line):
		try:
			tree = LineReader(given_line=line).get_input_tree()
			if isinstance(tree,Stop):
				return None
			rp = self.evaluate_tree(tree)
			if isinstance(rp,LazyPrint):
				rp.print() # error messages get raised, but ultimately have to be printed somewhere if not caught? idk
		except AntlrException as e:
			print("\t!! REPL failed to run initiating line:",line)
			print("\t    --got antlr exception:",e.msg)
		return None

	def assigned_to_top(self,res,env):
		if env is self.env:
			return True
		# we are now definitely inside some file, the question is whether we have taken
		# the result and kept it in the top level too, i.e., whether we have imported a non-private value.
		# checking whether it is also in self.env, even identical, will not tell us much as it may have been here and the same
		# already. so we have to replicate the logic here.
		if not isinstance(res,NamedVal):
			return False # only namedvals get set to begin with
		if res.name.startswith("_") or (res.name=="out"):
			return False
		return True

	def evaluate_tree(self,tree,env=None):
		if None is env: 
			env = self.env # otherwise, can pass custom env 
			# (e.g. when loading from a file, make env for that file, 
			# to keep that file's private (i.e. underscore-prefixed) variables to itself)
		if None is tree:
			return ResultToPrint(None,False)
		try:
			if tree.replstatement():
				return self.evaluate_replstatement(tree.replstatement())
			elif tree.raspstatement(): 
				res = Evaluator(env,self).evaluate(tree.raspstatement())
				if isinstance(res,NamedValList):
					return [ResultToPrint(r,self.assigned_to_top(r,env)) for r in res.nvs]
				return ResultToPrint(res, self.assigned_to_top(res,env)) 
		except (UndefinedVariable, ReservedName) as e:
			return LazyPrint("\t\t!!ignoring input:\n\t",e)
		except NotImplementedError:
			return LazyPrint("not implemented this command yet! ignoring")
		except (ArgsError,RASPTypeError,LoadError,RASPValueError) as e:
			return LazyPrint("\t\t!!ignoring input:\n\t",e)
		# if not replstatement or raspstatement, then comment
		return ResultToPrint(None,False)

	def filter_and_dump_prints(self):
		# TODO: some error messages are still rising up and getting printed before reaching this position :(
		def filter_named_val_reps(rps):
			# do the filtering. no namedvallists here - those are converted into a list of ResultToPrint s 
			# containing NamedVal s immediately after receiving them in evaluate_tree
			res = []
			names = set()
			for r in rps[::-1]: # go backwards - want to print the last occurence of each named item, not first, so filter works backwards
				if isinstance(r.res,NamedVal):
					if r.res.name in names:
						continue
					names.add(r.res.name)
				res.append(r)
			return res[::-1] # flip back forwards

		if not True in [isinstance(v,LazyPrint) for v in self.results_to_print]:
			self.results_to_print = filter_named_val_reps(self.results_to_print)
		# if isinstance(res,NamedVal):
		# self.print_named_val(res.name,res.val)
		#
		# print all that needs to be printed:
		for r in self.results_to_print:
			if isinstance(r,LazyPrint):
				r.print()
			else:
				self.print_result(r)
		# clear the list
		self.results_to_print = []




	def run(self,fromfile=None,env=None,store_prints=False):
		def careful_print(*a,**kw):
			if store_prints:
				self.results_to_print.append(LazyPrint(*a,**kw))
			else:
				print(*a,**kw)
		while True:
			try:
				tree = self.get_tree(fromfile)
				if isinstance(tree,Stop):
					break
				rp = self.evaluate_tree(tree,env)
				if store_prints:
					if isinstance(rp,list):
						self.results_to_print += rp # multiple results given - a multi-assignment
					else:
						self.results_to_print.append(rp)
				else:
					self.print_result(rp)
			except RASPTypeError as e:
				careful_print("\t!!statement executed, but result fails on evaluation:\n\t\t",e)
			except EOFError:
				careful_print("")
				break
			except StopException:
				break
			except KeyboardInterrupt:
				careful_print("")	# makes newline	
			except Exception as e:
				if debug:
					raise e
				careful_print("something went wrong:",e)




from antlr4.error.ErrorListener import ErrorListener


class AntlrException(Exception):
	def __init__(self,msg):
		self.msg = msg

class InputNotFinished(Exception):
	def __init__(self):
		pass

class MyErrorListener( ErrorListener ):
	def __init__(self):
		super(MyErrorListener, self).__init__()

	def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
		if offendingSymbol and offendingSymbol.text == "<EOF>":
			raise InputNotFinished()
		if msg.startswith("missing ';' at"):
			raise InputNotFinished()
		if "mismatched input" in msg:
			a=str(offendingSymbol)
			b=a[a.find("=")+2:]
			c=b[:b.find(",<")-1]
		ae = AntlrException(msg)
		ae.recognizer, ae.offendingSymbol, ae.line, ae.column, ae.msg, ae.e = recognizer, offendingSymbol, line, column, msg, e
		raise ae

	# def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
		# raise AntlrException("ambiguity")

	# def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
		# we're ok with this: happens with func defs it seems

	# def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
		# we're ok with this: happens with func defs it seems
		
class Stop:
	def __init__(self):
		pass

class LineReader:
	def __init__(self,prompt=">>",fromfile=None,given_line=None):
		self.fromfile = fromfile
		self.given_line = given_line
		self.prompt = prompt + " "
		self.cont_prompt = "."*len(prompt)+" "

	def str_to_antlr_parser(self,s):
		antlrinput = InputStream(s)
		lexer = RASPLexer(antlrinput)    
		lexer.removeErrorListeners()
		lexer.addErrorListener( MyErrorListener() )    
		stream = CommonTokenStream(lexer)        
		parser = RASPParser(stream) 
		parser.removeErrorListeners()     
		parser.addErrorListener( MyErrorListener() ) 
		return parser


	def read_line(self,continuing=False,nest_depth=0):
		prompt = self.cont_prompt if continuing else self.prompt
		if not None is self.fromfile:
			res = self.fromfile.readline()
			if not res: # python files return "" on last line (as opposed to "\n" on empty lines)
				return Stop()
			return res
		if not None is self.given_line:
			res = self.given_line
			self.given_line = Stop()
			return res
		else:
			return input(prompt+("  "*nest_depth))
			

	def get_input_tree(self):
		pythoninput=""
		multiline = False
		while True:
			newinput = self.read_line(continuing=multiline,
								nest_depth=pythoninput.split().count("def"))
			if isinstance(newinput,Stop): # input stream ended
				return Stop()
			if is_comment(newinput):
				newinput = "" # don't let comments get in and ruin things somehow
			pythoninput += newinput # don't replace newlines! this is how in-function comments get broken .replace("\n","")+" "
			parser = self.str_to_antlr_parser(pythoninput)
			try:
				res = parser.r().statement()
				if isinstance(res,list):
					# TODO: this seems to happen when there's ambiguity. figure out what is going on!!
					assert len(res)==1
					res = res[0]
				return res
			except InputNotFinished:
				multiline = True
				pythoninput+=" "



def print_seq(example,seq,still_on_prev_line=False,extra_pref="",lastpref_if_shortprint=""):
	if len(set(seq.get_vals()))==1:
		print(extra_pref if not still_on_prev_line else "",
				lastpref_if_shortprint,
				str(seq),end=" ") 
		print("[skipped full display: identical values]")# when there is only one value, it's nicer to just print that than the full list, verbosity be damned
		return
	if still_on_prev_line:
		print("")

	seq = seq.get_vals()
	def cleanboolslist(seq):
		if isinstance(seq[0],bool):
			tstr = "T" if seq.count(True) <= seq.count(False) else ""
			fstr = "F" if seq.count(False) <= seq.count(True) else ""
			return [tstr if v else fstr for v in seq]
		else:
			return seq

	example = cleanboolslist(example)
	seqtype = lazy_type_check(seq)
	seq = cleanboolslist(seq)
	example = [str(v) for v in example]
	seq = [str(v) for v in seq]
	maxlen = max(len(v) for v in example+seq)


	def neatline(seq):
		def padded(s):
			return " "*(maxlen-len(s))+s
		return " ".join(padded(v) for v in seq)
	print(extra_pref,"\t\tinput:  ",neatline(example),"\t","("+lazy_type_check(example)+"s)")
	print(extra_pref,"\t\toutput: ",neatline(seq),"\t","("+seqtype+"s)")

def print_select(example,select,extra_pref=""):
	# .replace("\n","\n\t\t\t")
	def nice_matrix_line(m):
		return " ".join("1" if v else " " for v in m)
	print(extra_pref,"\t\t\t    "," ".join(str(v) for v in example))
	matrix = select.get_vals()
	[print(extra_pref,"\t\t\t",v,"|",nice_matrix_line(matrix[m])) for v,m in zip(example,matrix)]


if __name__ == "__main__":
	REPL().run()

def runner():
	a = REPL()
	try:
		a.run()
	except Exception as e:
		print(e)
		return a,e
	return a,None
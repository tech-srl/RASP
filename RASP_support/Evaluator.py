from FunctionalSupport import select, zipmap, aggregate, \
	or_selects, and_selects, not_select, indices, \
	Unfinished, UnfinishedSequence, UnfinishedSelect
from Sugar import tplor, tpland, tplnot, toseq, full_s
from Support import RASPTypeError, RASPError
from collections.abc import Iterable
from zzantlr.RASPParser import RASPParser

ENCODER_NAME = "s-op"


def strdesc(o, desc_cap=None):
	if isinstance(o, Unfinished):
		return o.name
	if isinstance(o, list):
		res = "["+", ".join([strdesc(v) for v in o])+"]"
		if desc_cap is not None and len(res) > desc_cap:
			return "(list)"
		else:
			return res
	if isinstance(o, dict):
		res = "{"+", ".join((strdesc(k)+": "+strdesc(o[k])) for k in o)+"}"
		if desc_cap is not None and len(res) > desc_cap:
			return "(dict)"
		else:
			return res
	else:
		if isinstance(o, str):
			return "\""+o+"\""
		else:
			return str(o)


class RASPValueError(RASPError):
	def __init__(self, *a):
		super().__init__(*a)


DEBUG = False


def debprint(*a, **kw):
	if DEBUG:
		print(*a, **kw)


def ast_text(ast):  # just so don't have to go remembering this somewhere
	# consider seeing if can make it add spaces between the tokens when doing
	# this tho
	return ast.getText()


def isatom(v):
	# the legal atoms
	return True in [isinstance(v, t) for t in [int, float, str, bool]]


def name_general_type(v):
	if isinstance(v, list):
		return "list"
	if isinstance(v, dict):
		return "dict"
	if isinstance(v, UnfinishedSequence):
		return ENCODER_NAME
	if isinstance(v, UnfinishedSelect):
		return "selector"
	if isinstance(v, RASPFunction):
		return "function"
	if isatom(v):
		return "atom"
	return "??"


class ArgsError(Exception):
	def __init__(self, name, expected, got):
		super().__init__("wrong number of args for "+name +
						 "- expected: "+str(expected)+", got: "+str(got)+".")


class NamedVal:
	def __init__(self, name, val):
		self.name = name
		self.val = val


class NamedValList:
	def __init__(self, namedvals):
		self.nvs = namedvals


class JustVal:
	def __init__(self, val):
		self.val = val


class RASPFunction:
	def __init__(self, name, enclosing_env, argnames, statement_trees,
				 returnexpr, creator_name):
		self.name = name  # just for debug purposes
		self.enclosing_env = enclosing_env
		self.argnames = argnames
		self.statement_trees = statement_trees
		self.returnexpr = returnexpr
		self.creator = creator_name

	def __str__(self):
		return self.creator + " function: " + self.name \
			+ "(" + ", ".join(self.argnames) + ")"

	def __call__(self, *args):
		top_eval = args[-1]
		args = args[:-1]
		# nesting, because function shouldn't affect the enclosing environment
		env = self.enclosing_env.make_nested([])
		if not len(args) == len(self.argnames):
			raise ArgsError(self.name, len(self.argnames), len(args))
		for n, v in zip(self.argnames, args):
			env.set_variable(n, v)
		evaluator = Evaluator(env, top_eval.repl)
		for at in self.statement_trees:
			evaluator.evaluate(at)
		res = evaluator.evaluateExprsList(self.returnexpr)
		return res[0] if len(res) == 1 else res


class Evaluator:
	def __init__(self, env, repl):
		self.env = env
		self.sequence_running_example = repl.sequence_running_example
		self.backup_example = None
		# allows evaluating something that maybe doesn't necessarily work with
		# the main running example, but we just want to see what happens on
		# it - e.g. so we can do draw(tokens_int+1,[1,2]) without error even
		# while the main example is still "hello"
		self.repl = repl

	def evaluate(self, ast):
		if ast.expr():
			return self.evaluateExpr(ast.expr(), from_top=True)
		if ast.assign():
			return self.assign(ast.assign())
		if ast.funcDef():
			return self.funcDef(ast.funcDef())
		if ast.draw():
			return self.draw(ast.draw())
		if ast.forLoop():
			return self.forLoop(ast.forLoop())
		if ast.loadFile():
			return self.repl.loadFile(ast.loadFile(), self.env)

		# more to come
		raise NotImplementedError

	def draw(self, ast):
		# TODO: make at least some rudimentary comparisons of selectors somehow
		# to merge heads idk?????? maybe keep trace of operations used to
		# create them and those with exact same parent s-ops and operations
		# can get in? would still find eg select(0,0,==) and select(1,1,==)
		# different, but its better than nothing at all
		example = self.evaluateExpr(
			ast.inputseq) if ast.inputseq else self.sequence_running_example
		prev_backup = self.backup_example
		self.backup_example = example
		unf = self.evaluateExpr(ast.unf)
		if not isinstance(unf, UnfinishedSequence):
			raise RASPTypeError("draw expects unfinished sequence, got:", unf)
		unf.draw_comp_flow(example)
		res = unf(example)
		res.created_from_input = example
		self.backup_example = prev_backup
		return JustVal(res)

	def assign(self, ast):
		def set_val_and_name(val, name):
			self.env.set_variable(name, val)
			if isinstance(val, Unfinished):
				val.setname(name)  # completely irrelevant really for the REPL,
				# but will help maintain sanity when printing computation flows
			return NamedVal(name, val)

		varnames = self._names_list(ast.var)
		values = self.evaluateExprsList(ast.val)
		if len(values) == 1:
			values = values[0]

		if len(varnames) == 1:
			return set_val_and_name(values, varnames[0])
		else:
			if not len(varnames) == len(values):
				raise RASPTypeError("expected", len(
					varnames), "values, but got:", len(values))
			reslist = []
			for v, name in zip(values, varnames):
				reslist.append(set_val_and_name(v, name))
			return NamedValList(reslist)

	def _names_list(self, ast):
		idsList = self._get_first_cont_list(ast)
		return [i.text for i in idsList]

	def _set_iterator_and_vals(self, iterator_names, iterator_vals):
		if len(iterator_names) == 1:
			self.env.set_variable(iterator_names[0], iterator_vals)
		elif isinstance(iterator_vals, Iterable) \
				and (len(iterator_vals) == len(iterator_names)):
			for n, v in zip(iterator_names, iterator_vals):
				self.env.set_variable(n, v)
		else:
			if not isinstance(iterator_vals, Iterable):
				raise RASPTypeError(
					"iterating with multiple iterator names, but got single"
					+ " iterator value:", iterator_vals)
			else:
				# should work out by logic of last failed elif
				assert not (len(iterator_vals) == len(iterator_names)
							), "something wrong with Evaluator logic"
				raise RASPTypeError("iterating with", len(iterator_names),
									"names but got", len(iterator_vals),
									"values (", iterator_vals, ")")

	def _evaluateDictComp(self, ast):
		ast = ast.dictcomp
		d = self.evaluateExpr(ast.iterable)
		if not (isinstance(d, list) or isinstance(d, dict)):
			raise RASPTypeError(
				"dict comprehension should have got a list or dict to loop "
				+ "over, but got:", l)
		res = {}
		iterator_names = self._names_list(ast.iterator)
		for vals in d:
			orig_env = self.env
			self.env = self.env.make_nested()
			self._set_iterator_and_vals(iterator_names, vals)
			key = self.make_dict_key(ast.key)
			res[key] = self.evaluateExpr(ast.val)
			self.env = orig_env
		return res

	def _evaluateListComp(self, ast):
		ast = ast.listcomp
		seq = self.evaluateExpr(ast.iterable)
		if not (isinstance(seq, list) or isinstance(seq, dict)):
			raise RASPTypeError(
				"list comprehension should have got a list or dict to loop "
				+ "over, but got:", seq)
		res = []
		iterator_names = self._names_list(ast.iterator)
		for vals in seq:
			orig_env = self.env
			self.env = self.env.make_nested()
			# sets inside the now-nested env -
			self._set_iterator_and_vals(iterator_names, vals)
			# don't want to keep the internal iterators after finishing this
			# list comp
			res.append(self.evaluateExpr(ast.val))
			self.env = orig_env
		return res

	def forLoop(self, ast):
		iterator_names = self._names_list(ast.iterator)
		iterable = self.evaluateExpr(ast.iterable)
		if not (isinstance(iterable, list) or isinstance(iterable, dict)):
			raise RASPTypeError(
				"for loop needs to iterate over a list or dict, but got:",
				iterable)
		statements = self._get_first_cont_list(ast.mainbody)
		for vals in iterable:
			self._set_iterator_and_vals(iterator_names, vals)
			for s in statements:
				self.evaluate(s)
		return JustVal(None)

	def _get_first_cont_list(self, ast):
		res = []
		while ast:
			if ast.first:
				res.append(ast.first)
				# sometimes there's no first cause it's just eating a comment
			ast = ast.cont
		return res

	def funcDef(self, ast):
		funcname = ast.name.text
		argname_trees = self._get_first_cont_list(ast.arguments)
		argnames = [a.text for a in argname_trees]
		statement_trees = self._get_first_cont_list(ast.mainbody)
		returnexpr = ast.retstatement.res
		res = RASPFunction(funcname, self.env, argnames,
						   statement_trees, returnexpr, self.env.name)
		self.env.set_variable(funcname, res)
		return NamedVal(funcname, res)

	def _evaluateUnaryExpr(self, ast):
		uexpr = self.evaluateExpr(ast.uexpr)
		uop = ast.uop.text
		if uop == "not":
			if isinstance(uexpr, UnfinishedSequence):
				return tplnot(uexpr)
			elif isinstance(uexpr, UnfinishedSelect):
				return not_select(uexpr)
			else:
				return not uexpr
		if uop == "-":
			return -uexpr
		if uop == "+":
			return +uexpr
		if uop == "round":
			return round(uexpr)
		if uop == "indicator":
			if isinstance(uexpr, UnfinishedSequence):
				name = "I("+uexpr.name+")"
				zip = zipmap(uexpr, lambda a: 1 if a else 0, name=name)
				return zip.allow_suppressing_display()
				# naming res makes RASP think it is important, i.e.,
				# must always be displayed. but here it has only been named for
				# clarity, so correct RASP using .allow_suppressing_display()

			raise RASPTypeError(
				"indicator operator expects "+ENCODER_NAME+", got:", uexpr)
		raise NotImplementedError

	def _evaluateRange(self, ast):
		valsList = self.evaluateExprsList(ast.rangevals)
		if not len(valsList) in [1, 2, 3]:
			raise RASPTypeError(
				"wrong number of inputs to range, expected: 1, 2, or 3, got:",
				len(valsList))
		for v in valsList:
			if not isinstance(v, int):
				raise RASPTypeError(
					"range expects all integer inputs, but got:",
					strdesc(valsList))
		return list(range(*valsList))

	def _index_into_dict(self, d, index):
		if not isatom(index):
			raise RASPTypeError(
				"index into dict has to be atom"
				+ " (i.e., string, int, float, bool), got:", strdesc(index))
		if index not in d:
			raise RASPValueError("index [", strdesc(index), "] not in dict.")
		else:
			return d[index]

	def _index_into_list_or_str(self, seq, index):
		lname = "list" if isinstance(seq, list) else "string"
		if not isinstance(index, int):
			raise RASPTypeError("index into", lname,
								"has to be integer, got:", strdesc(index))
		if index >= len(seq) or (-index) > len(seq):
			raise RASPValueError(
				"index", index, "out of range for", lname, "of length",
				len(seq))
		return seq[index]

	def _index_into_sequence(self, s, index):
		if isinstance(index, int):
			if index >= 0:
				sel = select(toseq(index), indices, lambda q,
							 k: q == k, name="load from "+str(index))
			else:
				length = self.env.get_variable("length")
				real_index = length + index
				real_index.setname(length.name+str(index))
				sel = select(real_index, indices, lambda q,
							 k: q == k, name="load from "+str(index))
			agg = aggregate(sel, s, name=s.name+"["+str(index)+"]")
			return agg.allow_suppressing_display()
		else:
			raise RASPValueError(
				"index into sequence has to be integer, got:", strdesc(index))

	def _evaluateIndexing(self, ast):
		indexable = self.evaluateExpr(ast.indexable)
		index = self.evaluateExpr(ast.index)

		if isinstance(indexable, list) or isinstance(indexable, str):
			return self._index_into_list_or_str(indexable, index)
		elif isinstance(indexable, dict):
			return self._index_into_dict(indexable, index)
		elif isinstance(indexable, UnfinishedSequence):
			return self._index_into_sequence(indexable, index)
		else:
			raise RASPTypeError("can only index into a list, dict, string, or"
								+ " sequence, but instead got:",
								strdesc(indexable))

	def _evaluateSelectExpr(self, ast):
		key = self.evaluateExpr(ast.key)
		query = self.evaluateExpr(ast.query)
		sop = ast.selop.text
		key = toseq(key)  # in case got an atom in one of these,
		query = toseq(query)  # e.g. selecting 0th index: indices @= 0
		if sop == "<":
			return select(query, key, lambda q, k: q > k)
		if sop == ">":
			return select(query, key, lambda q, k: q < k)
		if sop == "==":
			return select(query, key, lambda q, k: q == k)
		if sop == "!=":
			return select(query, key, lambda q, k: not (q == k))
		if sop == "<=":
			return select(query, key, lambda q, k: q >= k)
		if sop == ">=":
			return select(query, key, lambda q, k: q <= k)

	def _evaluateBinaryExpr(self, ast):
		def has_sequence(seq, r):
			return isinstance(seq, UnfinishedSequence) \
				or isinstance(r, UnfinishedSequence)

		def has_selector(seq, r):
			return isinstance(seq, UnfinishedSelect) \
				or isinstance(r, UnfinishedSelect)

		def both_selectors(seq, r):
			return isinstance(seq, UnfinishedSelect) \
				and isinstance(r, UnfinishedSelect)
		left = self.evaluateExpr(ast.left)
		right = self.evaluateExpr(ast.right)
		bop = ast.bop.text
		bad_pair = RASPTypeError(
			"Cannot apply and/or between selector and non-selector")
		if bop == "and":
			if has_sequence(left, right):
				if has_selector(left, right):
					raise bad_pair
				return tpland(left, right)
			elif has_selector(left, right):
				if not both_selectors(left, right):
					raise bad_pair
				return and_selects(left, right)
			else:
				return (left and right)
		elif bop == "or":
			if has_sequence(left, right):
				if has_selector(left, right):
					raise bad_pair
				return tplor(left, right)
			elif has_selector(left, right):
				if not both_selectors(left, right):
					raise bad_pair
				return or_selects(left, right)
			else:
				return (left or right)
		if has_selector(left, right):
			raise RASPTypeError("Cannot apply", bop, "to selector(s)")
		elif bop == "+":
			return left + right
		elif bop == "-":
			return left - right
		elif bop == "*":
			return left * right
		elif bop == "/":
			return left/right
		elif bop == "^":
			return pow(left, right)
		elif bop == '%':
			return left % right
		elif bop == "==":
			return left == right
		elif bop == "<=":
			return left <= right
		elif bop == ">=":
			return left >= right
		elif bop == "<":
			return left < right
		elif bop == ">":
			return left > right
		# more, like modulo and power and all the other operators, to come
		raise NotImplementedError

	def _evaluateStandalone(self, ast):
		if ast.anint:
			return int(ast.anint.text)
		if ast.afloat:
			return float(ast.afloat.text)
		if ast.astring:
			return ast.astring.text[1:-1]
		raise NotImplementedError

	def _evaluateTernaryExpr(self, ast):
		cond = self.evaluateExpr(ast.cond)
		if isinstance(cond, Unfinished):
			res1 = self.evaluateExpr(ast.res1)
			res2 = self.evaluateExpr(ast.res2)
			cond, res1, res2 = tuple(map(toseq, (cond, res1, res2)))
			return zipmap((cond, res1, res2), lambda c, r1, r2: r1
						  if c else r2, name=res1.name+" if "+cond.name
						  + " else " + res2.name).allow_suppressing_display()
		else:
			return self.evaluateExpr(ast.res1) if cond \
				else self.evaluateExpr(ast.res2)
			# lazy eval when cond is non-unfinished allows legal loops over
			# actual atoms

	def _evaluateAggregateExpr(self, ast):
		sel = self.evaluateExpr(ast.sel)
		seq = self.evaluateExpr(ast.seq)
		seq = toseq(seq)  # just in case its an atom
		default = self.evaluateExpr(ast.default) if ast.default else None

		if not isinstance(sel, UnfinishedSelect):
			raise RASPTypeError("Expected selector, got:", strdesc(selector))
		if not isinstance(seq, UnfinishedSequence):
			raise RASPTypeError("Expected sequence, got:", strdesc(seq))
		if isinstance(default, Unfinished):
			raise RASPTypeError("Expected atom, got:", strdesc(default))
		return aggregate(sel, seq, default=default)

	def _evaluateZip(self, ast):
		list_exps = self._get_first_cont_list(ast.lists)
		lists = [self.evaluateExpr(e) for e in list_exps]
		if not lists:
			raise RASPTypeError("zip needs at least one list")
		for i, l in enumerate(lists):
			if not isinstance(l, list):
				raise RASPTypeError(
					"attempting to zip lists, but", i+1,
					"-th element is not list:", strdesc(l))
		n = len(lists[0])
		for i, l in enumerate(lists):
			if not len(l) == n:
				raise RASPTypeError("attempting to zip lists of length",
									n, ", but", i+1, "-th list has length",
									len(l))
		# keep everything lists, no tuples/lists mixing here, all the same to
		# rasp (no stuff like append etc)
		return [list(v) for v in zip(*lists)]

	def make_dict_key(self, ast):
		res = self.evaluateExpr(ast)
		if not isatom(res):
			raise RASPTypeError(
				"dictionary keys can only be atoms, but instead got:",
				strdesc(res))
		return res

	def _evaluateDict(self, ast):
		named_exprs_list = self._get_first_cont_list(ast.dictContents)
		return {self.make_dict_key(e.key): self.evaluateExpr(e.val)
				for e in named_exprs_list}

	def _evaluateList(self, ast):
		exprs_list = self._get_first_cont_list(ast.listContents)
		return [self.evaluateExpr(e) for e in exprs_list]

	def _evaluateApplication(self, ast, unf):
		input_vals = self._get_first_cont_list(ast.inputexprs)
		if not len(input_vals) == 1:
			raise ArgsError("evaluate unfinished", 1, len(input_vals))
		input_val = self.evaluateExpr(input_vals[0])
		if not isinstance(unf, Unfinished):
			raise RASPTypeError("Applying unfinished expects to apply",
								ENCODER_NAME, "or selector, got:",
								strdesc(sel))
		if not isinstance(input_val, Iterable):
			raise RASPTypeError(
				"Applying unfinished expects iterable input, got:",
				strdesc(input_val))
		res = unf(input_val)
		res.created_from_input = input_val
		return res

	def _evaluateRASPFunction(self, ast, raspfun):
		args_trees = self._get_first_cont_list(ast.inputexprs)
		args = tuple(self.evaluateExpr(t) for t in args_trees) + (self,)
		real_args = args[:-1]
		res = raspfun(*args)
		if isinstance(res, Unfinished):
			res.setname(
				raspfun.name+"("+" , ".join(strdesc(a, desc_cap=20)
											for a in real_args)+")")
		return res

	def _evaluateContains(self, ast):
		contained = self.evaluateExpr(ast.contained)
		container = self.evaluateExpr(ast.container)
		container_name = ast.container.var.text if ast.container.var \
			else str(container)
		if isinstance(contained, UnfinishedSequence):
			if not isinstance(container, list):
				raise RASPTypeError("\"["+ENCODER_NAME+"] in X\" expects X to"
									+ "be list of atoms, but got non-list:",
									strdesc(container))
			for v in container:
				if not isatom(v):
					raise RASPTypeError("\"["+ENCODER_NAME+"] in X\" expects X"
										+ "to be list of atoms, but got list "
										+ "with values:", strdesc(container))
			return zipmap(contained, lambda c: c in container,
						  name=contained.name + " in "
						  + container_name).allow_suppressing_display()
		elif isatom(contained):  # contained is now an atom
			if isinstance(container, list):
				return contained in container
			elif isinstance(container, UnfinishedSequence):
				indicator = zipmap(container, lambda v: int(v == contained))
				return aggregate(full_s, indicator) > 0
			else:
				raise RASPTypeError(
					"\"[atom] in X\" expects X to be list or " + ENCODER_NAME
					+ ", but got:", strdesc(container))
		if isinstance(contained, UnfinishedSelect) or isinstance(contained,
																 RASPFunction):
			obj_name = "select" if isinstance(
				contained, UnfinishedSelect) else "function"
			raise RASPTypeError("don't check if", obj_name,
								"is contained in list/dict: unless exact same "
								+ "instance, unable to check equivalence of",
								obj_name + "s")
		else:
			raise RASPTypeError("\"A in X\" expects A to be",
								ENCODER_NAME, "or atom, but got A:",
								strdesc(contained))

	def _evaluateLen(self, ast):
		singleList = self.evaluateExpr(ast.singleList)
		if not isinstance(singleList, list) or isinstance(singleList, dict):
			raise RASPTypeError(
				"attempting to compute length of non-list:",
				strdesc(singleList))
		return len(singleList)

	def evaluateExprsList(self, ast):
		exprsList = self._get_first_cont_list(ast)
		return [self.evaluateExpr(v) for v in exprsList]

	def _test_res(self, res):
		if isinstance(res, Unfinished):
			def succeeds_with(exampe):
				try:
					res(example, just_pass_exception_up=True)
				except:
					return False
				else:
					return True
			succeeds_with_backup = (self.backup_example is not None) and \
				succeeds_with(self.backup_example)
			if succeeds_with_backup:
				return
			succeeds_with_main = succeeds_with(self.sequence_running_example)
			if succeeds_with_main:
				return
			example = self.sequence_running_example if self.backup_example \
				is None else self.backup_example
			res(example, just_pass_exception_up=True)

	def evaluateExpr(self, ast, from_top=False):
		def format_return(res, resname="out",
						  is_application_of_unfinished=False):
			ast.evaled_value = res
			# run a quick test of the result (by attempting to evaluate it on
			# an example) to make sure there hasn't been some weird type
			# problem, so it shouts even before someone actively tries to
			# evaluate it
			self._test_res(res)

			if is_application_of_unfinished:
				return JustVal(res)
			else:
				self.env.set_out(res)
				if from_top:
					# this is when an expression has been evaled
					return NamedVal(resname, res)
				else:
					return res
		if ast.bracketed:  # in parentheses - get out of them
			return self.evaluateExpr(ast.bracketed, from_top=from_top)
		if ast.var:  # calling single variable
			varname = ast.var.text
			return format_return(self.env.get_variable(varname),
								 resname=varname)
		if ast.standalone:
			return format_return(self._evaluateStandalone(ast.standalone))
		if ast.bop:
			return format_return(self._evaluateBinaryExpr(ast))
		if ast.uop:
			return format_return(self._evaluateUnaryExpr(ast))
		if ast.cond:
			return format_return(self._evaluateTernaryExpr(ast))
		if ast.aggregate:
			return format_return(self._evaluateAggregateExpr(ast.aggregate))
		if ast.unfORfun:

			# before evaluating the unfORfun expression,
			# consider that it may be an unf that would not work
			# with the current running example, and allow that it may have
			# been sent in with an example for which it will work
			prev_backup = self.backup_example
			input_vals = self._get_first_cont_list(ast.inputexprs)
			if len(input_vals) == 1:
				self.backup_example = self.evaluateExpr(input_vals[0])

			unfORfun = self.evaluateExpr(ast.unfORfun)

			self.backup_example = prev_backup

			if isinstance(unfORfun, Unfinished):
				return format_return(self._evaluateApplication(ast, unfORfun),
									 is_application_of_unfinished=True)
			elif isinstance(unfORfun, RASPFunction):
				return format_return(self._evaluateRASPFunction(ast, unfORfun))
		if ast.selop:
			return format_return(self._evaluateSelectExpr(ast))
		if ast.aList():
			return format_return(self._evaluateList(ast.aList()))
		if ast.aDict():
			return format_return(self._evaluateDict(ast.aDict()))
		if ast.indexable:  # indexing into a list, dict, or s-op
			return format_return(self._evaluateIndexing(ast))
		if ast.rangevals:
			return format_return(self._evaluateRange(ast))
		if ast.listcomp:
			return format_return(self._evaluateListComp(ast))
		if ast.dictcomp:
			return format_return(self._evaluateDictComp(ast))
		if ast.container:
			return format_return(self._evaluateContains(ast))
		if ast.lists:
			return format_return(self._evaluateZip(ast))
		if ast.singleList:
			return format_return(self._evaluateLen(ast))
		raise NotImplementedError


# new ast getText function for expressions
def new_getText(self):  # original getText function stored as self._getText
	if hasattr(self, "evaled_value") and isatom(self.evaled_value):
		return str(self.evaled_value)
	else:
		return self._getText()


RASPParser.ExprContext._getText = RASPParser.ExprContext.getText
RASPParser.ExprContext.getText = new_getText

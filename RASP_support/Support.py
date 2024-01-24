# dont let them mutate the things i'm allowing them to have as vals
from copy import deepcopy
import pprint


class RASPError(Exception):
	def __init__(self, *a):
		super().__init__(" ".join([str(b) for b in a]))


class RASPTypeError(RASPError):
	def __init__(self, *a):
		super().__init__(*a)


def clean_val(num, digits=3):  # taken from my helper functions
	res = round(num, digits)
	if digits == 0:
		res = int(res)
	return res


class SupportException(Exception):
	def __init__(self, m):
		Exception.__init__(self, m)


TBANNED = "banned"
TMISMATCHED = "mismatched"
TNAME = {bool: "bool", str: "string", int: "int", float: "float"}
NUMTYPES = [TNAME[int], TNAME[float]]
sorted_typenames_list = sorted(list(TNAME.values()))
legal_types_list_string = ", ".join(
	sorted_typenames_list[:-1])+" or "+sorted_typenames_list[-1]


def is_in_types(v, tlist):
	for t in tlist:
		if isinstance(v, t):
			return True
	return False


def lazy_type_check(vals):
	legal_val_types = [str, bool, int, float]
	number_types = [int, float]

	# all vals are same, legal, type:
	for t in legal_val_types:
		b = [isinstance(v, t) for v in vals]
		if False not in b:
			return TNAME[t]

	# allow vals to also be mixed integers and ints, treat those as floats
	# (but don't actually change the ints to floats, want neat printouts)
	b = [is_in_types(v, number_types) for v in vals]
	if False not in b:
		return TNAME[float]

	# from here it's all bad, but lets have some clear error messages
	b = [is_in_types(v, legal_val_types) for v in vals]
	if False not in b:
		return TMISMATCHED  # all legal types, but mismatched
	else:
		return TBANNED


class Sequence:
	def __init__(self, vals):
		self.type = lazy_type_check(vals)
		if self.type == TMISMATCHED:
			raise RASPTypeError(
				"attempted to create sequence with vals of different types:"
				+ f"\n\t\t {vals}")
		if self.type == TBANNED:
			raise RASPTypeError(
				"attempted to create sequence with illegal val types "
				+ f"(vals must be {legal_types_list_string}):\n\t\t {vals}")
		self._vals = vals

	def __str__(self):
		# return "Sequence"+str([small_str(v) for v in self._vals])
		if (len(set(self._vals)) == 1) and (len(self._vals) > 1):
			res = "["+small_str(self._vals[0])+"]*"+str(len(self._vals))
		else:
			res = "["+", ".join(small_str(v) for v in self._vals)+"]"
		return res + " ("+self.type+"s)"

	def __repr__(self):
		return str(self)

	def __len__(self):
		return len(self._vals)

	def get_vals(self):
		return deepcopy(self._vals)


def dims_match(seqs, expected_dim):
	return False not in [expected_dim == len(seq) for seq in seqs]


class Select:
	def __init__(self, n, q_vars, k_vars, f):
		self.n = n
		self.makeselect(q_vars, k_vars, f)
		self.niceprint = None

	def get_vals(self):
		if self.select is None:
			self.makeselect()
		return deepcopy(self.select)

	def makeselect(self, q_vars=None, k_vars=None, f=None):
		if None is q_vars:
			assert (None is k_vars) and (None is f)
			q_vars = (Sequence(self.target_index),)
			k_vars = (Sequence(list(range(self.n))),)
			def f(t, i): return t == i
		self.select = {i: [f(*get(q_vars, i), *get(k_vars, j))
						   for j in range(self.n)]
					   for i in range(self.n)}  # outputs of f should be
		# True or False. j goes along input dim, i along output

	def __str__(self):
		self.get_vals()
		if None is self.niceprint:
			d = {i: list(map(int, self.select[i])) for i in self.select}
			self.niceprint = str(self.niceprint)
			if len(str(d)) > 40:
				starter = "\n"
				self.niceprint = pprint.pformat(d)
			else:
				starter = ""
				self.niceprint = str(d)
			self.niceprint = starter + self.niceprint
		return self.niceprint

	def __repr__(self):
		return str(self)


def select(n, q_vars, k_vars, f):
	return Select(n, q_vars, k_vars, f)

# applying selects or feedforward (map)


def aggregate(select, k_vars, func, default=None):
	return to_sequences(apply_average_select(select, k_vars, func, default))


def to_sequences(results_by_index):
	def totup(r):
		if not isinstance(r, tuple):
			return (r,)
		return r
	# convert scalar results to tuples of length 1
	results_by_index = list(map(totup, results_by_index))
	# one list (sequence) per output value
	results_by_output_val = list(zip(*results_by_index))
	res = tuple(map(Sequence, results_by_output_val))
	if len(res) == 1:
		return res[0]
	else:
		return res


def zipmap(n, k_vars, func):
	# assert len(k_vars) >= 1, "dont make a whole sequence for a plain constant
	# you already know the value of.."
	results_by_index = [func(*get(k_vars, i)) for i in range(n)]
	return to_sequences(results_by_index)


def verify_default_size(default, num_output_vars):
	assert num_output_vars > 0
	if num_output_vars == 1:
		errnote = "aggregates on functions with single output should have" \
			+ " scalar default"
		assert not isinstance(default, tuple), errnote
	elif num_output_vars > 1:
		errnote = "for function with >1 output values, default should be" \
			+ " tuple of default values, of equal length to passed" \
			+ " function's output values (for function with single output" \
			+ " value, default should be single value too)"
		check = isinstance(default, tuple) and len(default) == num_output_vars
		assert check, errnote


def apply_average_select(select, k_vars, func, default=0):
	def apply_func_to_each_index():
		# kvs is list [by index] of lists [by varname] of values
		kvs = [get(k_vars, i) for i in list(range(select.n))]
		candidate_i = [func(*kvi) for kvi in kvs]  # candidate output per index
		if num_output_vars > 1:
			candidates_by_varname = list(zip(*candidate_i))
		else:
			# expect tuples of values for conversions in return_sequences
			candidates_by_varname = (candidate_i,)
		return candidates_by_varname

	def prep_default(default, num_output_vars):
		if None is default:
			default = 0
			# output of average is always floats, so will be converting all
			# to floats here else we'll fail the lazy type check in the
			# Sequences. (and float(None) doesn't 'compile' )
			# TODO: maybe just lose the lazy type check?
		if not isinstance(default, tuple) and (num_output_vars > 1):
			default = tuple([default]*num_output_vars)
			# *specifically* in apply_average, where values have to be floats,
			# allow default to be single val,
			# that will be repeated for all wanted outputs
		verify_default_size(default, num_output_vars)
		if not isinstance(default, tuple):
			# specifically with how we're going to do things here in the
			# average aggregate, will help to actually have the outputs get 
			# passed around as tuples, even if they're scalars really.
			# but do this after the size check for the scalar one so it doesn't
			# get filled with weird ifs... this tupled scalar thing is only a 
			# convenience in this implementation in this here function
			default = (default,)
		return default

	def apply_and_average_single_index(outputs_by_varname, index,
									   index_scores, num_output_vars, default):
		def mean(scores, vals):
			n = scores.count(True)  # already >0 by earlier
			if n == 1:
				return vals[scores.index(True)]
			# else # n>1
			if not (lazy_type_check(vals) in NUMTYPES):
				raise Exception(
					"asked to average multiple values, but they are "
					+ "non-numbers: " + str(vals))
			return sum([v for s, v in zip(scores, vals) if s])*1.0/n

		num_influencers = index_scores.count(True)
		if num_influencers == 0:
			return default
		else:
			# return_sequences expects multiple outputs to be in tuple form
			return tuple(mean(index_scores, o_by_i)
						 for o_by_i in outputs_by_varname)
	num_output_vars = get_num_outputs(func(*get(k_vars, 0)))
	candidates_by_varname = apply_func_to_each_index()
	default = prep_default(default, num_output_vars)
	means_per_index = [apply_and_average_single_index(candidates_by_varname,
													  i, select.select[i],
													  num_output_vars, default)
					   for i in range(select.n)]
	# list (per index) of all the new variable values (per varname)
	return means_per_index


# user's responsibility to give functions that always have same number of
# outputs
def get_num_outputs(dummy_out):
	if isinstance(dummy_out, tuple):
		return len(dummy_out)
	return 1


def small_str(v):
	if isinstance(v, float):
		return str(clean_val(v, 3))
	if isinstance(v, bool):
		return "T" if v else "F"
	return str(v)


def get(vars_list, index):  # index should be within range to access
	# v._vals and if not absolutely should raise an error, as it will here
	# by the attempted access
	res = deepcopy([v._vals[index] for v in vars_list])
	return res

import functools
from copy import deepcopy # dont let them mutate the things i'm allowing them to have as vals
import pprint

class RASPError(Exception):
	def __init__(self,*a):
		super().__init__(" ".join([str(b) for b in a]))

class RASPTypeError(RASPError):
	def __init__(self,*a):
		super().__init__(*a)

def clean_val(num,digits=3): # taken from my helper functions
	res = round(num,digits)
	if digits == 0:
		res = int(res)
	return res

class SupportException(Exception):
	def __init__(self,m):
		Exception.__init__(self,m)

TBAD = "bad"
TBS = {bool:"bool",str:"str"}
TNUM = "num"

def _lazy_type_check(vals):
	def isnumber(v):
		return isinstance(v,int) or isinstance(v,float)

	for t in [str,bool]:
		b = [isinstance(v,t) for v in vals]
		if False not in b:
			return TBS[t]
	if False not in [isnumber(v) for v in vals]:
		return TNUM
	return TBAD

class Sequence:
	def __init__(self,vals):
		self.type = _lazy_type_check(vals)
		if self.type == TBAD:
			raise RASPTypeError("attempted to create sequence with vals of different types:",vals)
		self._vals = vals

	def __str__(self):
		# return "Sequence"+str([small_str(v) for v in self._vals])
		if (len(set(self._vals))==1) and (len(self._vals)>1):
			return "["+small_str(self._vals[0])+"]*"+str(len(self._vals))
		return "["+", ".join(small_str(v) for v in self._vals)+"]"

	def __repr__(self):
		return str(self)

	def __len__(self):
		return len(self._vals)

	def get_vals(self):
		return deepcopy(self._vals)


def dims_match(seqs,expected_dim):
	return False not in [expected_dim == len(seq) for seq in seqs]

class Select:
	def __init__(self, n, q_vars, k_vars, f):	
		self.n = n
		self.makeselect(q_vars,k_vars,f)
		self.niceprint = None

	def get_vals(self):
		if None is self.select:
			self.makeselect()
		return deepcopy(self.select)

	def makeselect(self,q_vars=None,k_vars=None,f=None):
		if None is q_vars:
			assert (None is k_vars) and (None is f)
			q_vars = (Sequence(self.target_index),) 
			k_vars = (Sequence(list(range(self.n))),)
			f = lambda t,i:t==i
		self.select = {i:[f(*get(q_vars,i),*get(k_vars,j)) for j in range(self.n)] 
									for i in range(self.n)} # outputs of f should be 
									# True or False. j goes along input dim, i along output

	def __str__(self):
		select = self.get_vals()
		if None is self.niceprint:
			d = {i:list(map(int,self.select[i])) for i in self.select}		
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

def select(n,q_vars,k_vars,f):
	return Select(n,q_vars,k_vars,f)

## applying selects or feedforward (map)
def aggregate(select,k_vars,func,default=None):
	return to_sequences(apply_average_select(select,k_vars,func,default))

def to_sequences(results_by_index):
	def totup(r):
		if not isinstance(r,tuple):
			return (r,)
		return r
	results_by_index = list(map(totup,results_by_index)) # convert scalar results to tuples of length 1
	results_by_output_val = list(zip(*results_by_index)) # one list (sequence) per output value
	res = tuple(map(Sequence,results_by_output_val))
	if len(res) == 1:
		return res[0]
	else:
		return res

def zipmap(n,k_vars,func):
	# assert len(k_vars) >= 1, "dont make a whole sequence for a plain constant you already know the value of.."
	results_by_index = [func(*get(k_vars,i)) for i in range(n)]
	return to_sequences(results_by_index)

def verify_default_size(default,num_output_vars):
	assert num_output_vars > 0
	if num_output_vars == 1:
		assert not isinstance(default,tuple), "aggregates on functions with single output should have scalar default"
	elif num_output_vars > 1:
		assert isinstance(default,tuple) and len(default)==num_output_vars,\
		 "for function with >1 output values, default should be tuple of default \
		 values, of equal length to passed function's output values (for function \
		 with single output value, default should be single value too)"

def apply_average_select(select,k_vars,func,default=0):
	def apply_func_to_each_index():
		kvs = [get(k_vars,i) for i in list(range(select.n))] # kvs is list [by index] of lists [by varname] of values
		candidate_i = [func(*kvi) for kvi in kvs] # candidate output per index
		if num_output_vars > 1:
			candidates_by_varname = list(zip(*candidate_i))
		else:
			candidates_by_varname = (candidate_i,) # expect tuples of values for conversions in return_sequences
		return candidates_by_varname

	def prep_default(default,num_output_vars):
		if None is default:
			default = 0
			# output of average is always floats, so will be converting all 
			# to floats here else we'll fail the lazy type check in the Sequences.
			# (and float(None) doesn't 'compile' )
			# TODO: maybe just lose the lazy type check?
		if not isinstance(default,tuple) and (num_output_vars>1):
			default = tuple([default]*num_output_vars) 
			# *specifically* in apply_average, where values have to be floats,
			# allow default to be single val, 
			#that will be repeated for all wanted outputs
		verify_default_size(default,num_output_vars)
		if not isinstance(default,tuple):
			default = (default,) # specifically with how we're going to do things here in the average aggregate,
			# will help to actually have the outputs get passed around as tuples, even if they're scalars really.
			# but do this after the size check for the scalar one so it doesn't get filled with weird ifs... this 
			# tupled scalar thing is only a convenience in this implementation in this here function
		return default

	def apply_and_average_single_index(outputs_by_varname,index,
									   index_scores,num_output_vars,default):
		def mean(scores,vals):
			n = scores.count(True) # already >0 by earlier
			if n == 1:
				return vals[scores.index(True)]
			# else # n>1
			if not _lazy_type_check(vals)==TNUM:
				raise Exception("asked to average multiple values, but they are non-numbers: "+str(vals))
			return sum([v for s,v in zip(scores,vals) if s])*1.0/n 
	
		num_influencers = index_scores.count(True)
		if num_influencers == 0:
			return default
		else:
			return tuple(mean(index_scores,o_by_i) for o_by_i in outputs_by_varname) # return_sequences expects multiple outputs to be in tuple form
	num_output_vars = get_num_outputs(func(*get(k_vars,0)))
	candidates_by_varname = apply_func_to_each_index()
	default = prep_default(default,num_output_vars)
	means_per_index = [apply_and_average_single_index(candidates_by_varname,
									i,select.select[i],num_output_vars,default) 
											for i in range(select.n)]
	# list (per index) of all the new variable values (per varname)
	return means_per_index

def get_num_outputs(dummy_out): # user's responsibility to give functions that always have same number of outputs
	if isinstance(dummy_out,tuple):
		return len(dummy_out)
	return 1

def small_str(v):
	if isinstance(v,float):
		return str(clean_val(v,3))
	if isinstance(v,bool):
		return "T" if v else "F"
	return str(v)


def get(vars_list,index): # index should be within range to access
# v._vals and if not absolutely should raise an error, as it will here
# by the attempted access
	res = deepcopy([v._vals[index] for v in vars_list])
	return res




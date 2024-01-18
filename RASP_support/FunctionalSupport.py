from Support import aggregate as _aggregate
from Support import Sequence, RASPTypeError
from Support import select as _select
from Support import zipmap as _zipmap
import traceback
import sys  # for readable exception handling
from collections.abc import Iterable
from copy import copy

name_maxlen = 30
plain_unfinished_name = "unf"
plain_unfinished_select_name = "sel"
plain_unfinished_sequence_name = "s-op"
plain_indices = "indices"
plain_tokens = "tokens"

debug = False

# unique ids for all Unfinished objects, numbered by order of creation. ends up
# very useful sometimes


class NextId:
	def __init__(self):
		self.i = 0

	def get_next(self):
		self.i += 1
		return self.i


unique_id_maker = NextId()


def creation_order_id():
	return unique_id_maker.get_next()


class AlreadyPrintedTheException:
	def __init__(self):
		self.b = False

	def __bool__(self):
		return self.b


global_printed = AlreadyPrintedTheException()

# various unfinished objects


class Unfinished:
	def __init__(self, parents_tuple, parents2self, name=plain_unfinished_name,
				 is_toplevel_input=False, min_poss_depth=-1):
		self.parents_tuple = parents_tuple
		self.parents2self = parents2self
		self.last_w = None
		self.last_res = None
		self.is_toplevel_input = is_toplevel_input
		self.setname(name if not self.is_toplevel_input else "input")
		self.creation_order_id = creation_order_id()
		self.min_poss_depth = min_poss_depth
		self._real_parents = None
		self._full_parents = None
		self._sorted_full_parents = None

	def setname(self, name, always_display_when_named=True):
		if name is not None:
			if len(name) > name_maxlen:
				if isinstance(self, UnfinishedSequence):
					name = plain_unfinished_sequence_name
				elif isinstance(self, UnfinishedSelect):
					name = plain_unfinished_select_name
				else:
					name = plain_unfinished_name
			self.name = name
			# if you set something's name, you probably want to see it
			self.always_display = always_display_when_named
		# return self to allow chaining with other calls and throwing straight
		# into a return statement etc
		return self

	def get_parents(self):
		if None is self._real_parents:
			real_parents_part1 = [
				p for p in self.parents_tuple if is_real_unfinished(p)]
			other_parents = [
				p for p in self.parents_tuple if not is_real_unfinished(p)]
			res = real_parents_part1
			for p in other_parents:
				# recursion: branch back through all the parents of the unf,
				# always stopping wherever hit something 'real' ie a select or
				# a sequence 
				res += p.get_parents()
			#  nothing is made from more than one select...
			assert len(
				[p for p in res if isinstance(p, UnfinishedSelect)]) <= 1
			self._real_parents = set(res)
		# in case someone messes with the list eg popping through it
		return copy(self._real_parents)

	def _flat_compute_full_parents(self):
		# TODO: take advantage of anywhere full_parents have already been
		# computed, tho, otherwise no point in doing the recursion ever
		explored = set()
		not_explored = set([self])
		while not_explored:
			p = not_explored.pop()
			if p in explored:
				# this may happen due to also adding things directly to
				# explored sometimes
				continue
			if None is not p._full_parents:
				# note that _full_parents include self
				explored.update(p._full_parents)
			else:
				new_parents = p.get_parents()
				explored.add(p)
				not_explored.update(new_parents)
		return explored

	def _recursive_compute_full_parents(self):
		res = self.get_parents()  # get_parents returns a copy
		res.update([self])  # full parents include self
		for p in self.get_parents():
			res.update(p.get_full_parents(recurse=True, trusted=True))
		return res

	def _sort_full_parents(self):
		if None is self._sorted_full_parents:
			self._sorted_full_parents = sorted(
				self._full_parents, key=lambda unf: unf.creation_order_id)

	def get_full_parents(self, recurse=False, just_compute=False,
						 trusted=False):
		# Note: full_parents include self
		if None is self._full_parents:
			if recurse:
				self._full_parents = self._recursive_compute_full_parents()
			else:
				self._full_parents = self._flat_compute_full_parents()
				# avoids recursion, and so avoids passing the max recursion
				# depth

				# but now having done that we would like to store the result
				# for all parents so we can take advantage of it in the future
				for p in self.get_sorted_full_parents():
					p.get_full_parents(recurse=True, just_compute=True)
					# have them all compute their full parents so they are
					# ready for the future, but only do this in sorted order, 
					# so recursion is always shallow. (always gets shorted with
					# self._full_parents, which is being computed here for each
					# unfinished starting from the top of the computation
					# graph)
		if not just_compute:
			if trusted:
				# functions where you have checked they don't modify the
				# returned result can be marked as trusted and get the true
				# _full_parents
				return self._full_parents
			else:
				# otherwise they get a copy
				return copy(self._full_parents)

	def get_sorted_full_parents(self):
		# could have just made get_full_parents give a sorted result, but
		# wanted a function where name is already clear that result will be
		# sorted, to avoid weird bugs in future. (especially that being not
		# sorted will only affect performance, and possibly break recursion
		# depth)

		if None is self._sorted_full_parents:
			if None is self._full_parents:
				self.get_full_parents(just_compute=True)
			self._sort_full_parents()
		return copy(self._sorted_full_parents)

	def __call__(self, w, print_all_named_sequences=False, print_input=False,
				 print_all_sequences=False, print_all=False, topcall=True,
				 just_pass_exception_up=False):
		if (not isinstance(w, Iterable)) or (not w):
			raise RASPTypeError(
				"RASP sequences/selectors expect non-empty iterables, got: "
				+ str(w))
		global_printed.b = False
		if w == self.last_w:
			return self.last_res  # don't print same calculation multiple times

		else:
			if self.is_toplevel_input:
				res = w
				self.last_w, self.last_res = w, w
			else:
				try:
					if topcall:
						# before doing the main call, evaluate all parents
						# (in order of dependencies, attainable by using
						# creation_order_id attribute), this avoids a deep
						# recursion: every element that is evaluated only has
						# to go back as far as its own 'real' (i.e., s-op or
						# selector) parents to hit something that has already
						# been evaluated, and then those will not recurse
						# further back as they use memoization
						for unf in self.get_sorted_full_parents():
							# evaluate
							unf(w, topcall=False,
								just_pass_exception_up=just_pass_exception_up)

					p_a_n_s = print_all_named_sequences
					j_p_e_u = just_pass_exception_up
					args = tuple(p(w,
								   print_all_named_sequences=p_a_n_s,
								   print_input=print_input,
								   print_all_sequences=print_all_sequences,
								   print_all=print_all,
								   topcall=False,
								   just_pass_exception_up=j_p_e_u)
								 for p in self.parents_tuple)
					res = self.parents2self(*args)
				except Exception as e:
					if just_pass_exception_up:
						raise e
					if isinstance(e, RASPTypeError):
						raise e
					if not global_printed.b:
						seperator = "=" * 63
						print(seperator)
						print(seperator)
						print("evaluation failed in: [", self.name,
							  "] with exception:\n", e)
						print(seperator)
						print("parent values are:")
						for p in self.parents_tuple:
							print("=============")
							print(p.name)
							print(p.last_res)
						print(seperator)
						print(seperator)
						a, b, tb = sys.exc_info()
						tt = traceback.extract_tb(tb)
						last_call = max([i for i, t in enumerate(tt)
										 if "__call__" in str(t)])
						print(''.join(traceback.format_list(tt[last_call+1:])))

						# traceback.print_exception(a,b,tb)

					global_printed.b = True

					if debug or not topcall:
						raise
					else:
						return "EVALUATION FAILURE"

				self.last_w, self.last_res = w, res

		def should_print():
			if isinstance(res, Sequence):
				if print_all_named_sequences and self.name not in plain_names:
					return True
				if print_all_sequences:
					return True
				if self.is_toplevel_input and print_input:
					return True
			return print_all
		if should_print():
			print("resolved \""+self.name +
				  (("\" from:\" "+str(self.get_own_root_input(w))+" \"")
				   if print_root_inputs_too else ""),
				  ":\n\t", res)
		return res


class UnfinishedSequence(Unfinished):
	def __init__(self, parents_tuple, parents2self,
				 name=plain_unfinished_sequence_name,
				 elementwise_function=None, default=None, min_poss_depth=0,
				 from_zipmap=False, output_index=-1,
				 definitely_uses_identity_function=False):
		# min_poss_depth=0 starts all of the base sequences (eg indices) off
		# right. 

		# might have got none from some default value, fix it before continuing
		# because later things eg DrawCompFlow will expect name to be str
		if name is None:
			name = plain_unfinished_sequence_name  
		super(UnfinishedSequence, self).__init__(parents_tuple,
												 parents2self, name=name,
												 min_poss_depth=min_poss_depth)
		# can be inferred (by seeing if there are parent selects), but this is
		# simple enough. helpful for rendering comp flow visualisations
		self.from_zipmap = from_zipmap
		# useful for analysis later
		self.elementwise_function = elementwise_function
		self.output_index = output_index
		# useful for analysis later
		self.default = default
		self.definitely_uses_identity_function = \
			definitely_uses_identity_function
		self.never_display = False
		self._constant = False

	def __str__(self):
		id = str(self.creation_order_id)
		return "UnfinishedSequence object, name: " + self.name + " id: " + id

	def mark_as_constant(self):
		self._constant = True
		return self

	def is_constant(self):
		return self._constant


class UnfinishedSelect(Unfinished):
	def __init__(self, parents_tuple, parents2self,
				 name=plain_unfinished_select_name, compare_string=None,
				 min_poss_depth=-1, q_vars=None, k_vars=None,
				 orig_selector=None):  # selects should be told their depth,
		# -1 will warn of problems properly
		if name is None:  # as in unfinishedsequence, some other function might
			# have passed in a None somewhere
			name = plain_unfinished_select_name  # so fix before a print goes
			# wrong
		super(UnfinishedSelect, self).__init__(parents_tuple,
											   parents2self, name=name,
											   min_poss_depth=min_poss_depth)
		self.compare_string = str(
			self.creation_order_id) if compare_string is None \
			else compare_string
		# they're not really optional i just dont want to add more mess to the
		# func
		assert None not in [q_vars, k_vars]
		self.q_vars = q_vars  # don't actually need them, but useful for
		self.k_vars = k_vars  # drawing comp flow
		# use compare string for comparison/uniqueness rather than overloading
		# __eq__ of unfinishedselect, to avoid breaking things in unknown
		# locations, and to be able to put selects in dictionaries and stuff
		# (overloading __eq__ makes an object unhasheable unless i guess you
		# overload the hash too?). need these comparisons for optimisations in
		# analysis eg if two selects are identical they can be same head
		self.orig_selector = orig_selector  # for comfortable compositions of
		# selectors

	def __str__(self):
		id = str(self.creation_order_id)
		return "UnfinishedSelect object, name: " + self.name + " id: " + id


# as opposed to intermediate unfinisheds like tuples of sequences
def is_real_unfinished(unf):
	return isinstance(unf, UnfinishedSequence) \
		or isinstance(unf, UnfinishedSelect)

# some tiny bit of sugar that fits here:


def is_sequence_of_unfinishedseqs(seqs):
	if not isinstance(seqs, Iterable):
		return False
	return False not in [isinstance(seq, UnfinishedSequence) for seq in seqs]


class BareBonesFunctionalSupportException(Exception):
	def __init__(self, m):
		Exception.__init__(self, m)


def to_tuple_of_unfinishedseqs(seqs):
	if is_sequence_of_unfinishedseqs(seqs):
		return tuple(seqs)
	if isinstance(seqs, UnfinishedSequence):
		return (seqs,)
	print("seqs:", seqs)
	raise BareBonesFunctionalSupportException(
		"input to select/aggregate not an unfinished sequence or sequence of"
		+ " unfinished sequences")


def tup2tup(*x):
	return tuple([*x])


class UnfinishedSequencesTuple(Unfinished):
	def __init__(self, parents_tuple, parents2self=None):
		# sequence tuples only exist in here, user doesn't 'see' them. can have
		# lots of default values they're just a convenience for me
		if parents2self is None:  # just sticking a bunch of unfinished
			# sequences together into one thing for reasons
			parents2self = tup2tup
			parents_tuple = to_tuple_of_unfinishedseqs(parents_tuple)
			assert is_sequence_of_unfinishedseqs(
				parents_tuple) and isinstance(parents_tuple, tuple)
		# else - probably creating several sequences at once from one aggregate
		super(UnfinishedSequencesTuple, self).__init__(
			parents_tuple, parents2self, name="plain unfinished tuple")

	def __add__(self, other):
		assert isinstance(other, UnfinishedSequencesTuple)
		assert self.parents2self is tup2tup
		assert other.parents2self is tup2tup
		return UnfinishedSequencesTuple(self.parents_tuple+other.parents_tuple)


_input = Unfinished((), None, is_toplevel_input=True)
# and now, the actual exposed functions
indices = UnfinishedSequence((_input,), lambda w: Sequence(
	list(range(len(w)))), name=plain_indices)
tokens_str = UnfinishedSequence((_input,), lambda w: Sequence(
	list(map(str, w))), name=plain_tokens+"_str")
tokens_int = UnfinishedSequence((_input,), lambda w: Sequence(
	list(map(int, w))), name=plain_tokens+"_int")
tokens_float = UnfinishedSequence((_input,), lambda w: Sequence(
	list(map(float, w))), name=plain_tokens+"_float")
tokens_bool = UnfinishedSequence((_input,), lambda w: Sequence(
	list(map(bool, w))), name=plain_tokens+"_bool")
tokens_asis = UnfinishedSequence(
	(_input,), lambda w: Sequence(w), name=plain_tokens+"_asis")
base_tokens = [tokens_str, tokens_int, tokens_float, tokens_bool, tokens_asis]


def _min_poss_depth(unfs):
	if isinstance(unfs, Unfinished):  # got single unfinished and not iterable
		# of them
		unfs = [unfs]
	# max b/c cant go less deep than deepest
	return max([u.min_poss_depth for u in unfs]+[0])
	# add that 0 thing so list is never empty and max complains.


def tupleise(v):
	if isinstance(v, tuple) or isinstance(v, list):
		return tuple(v)
	return (v,)


def select(q_vars, k_vars, selector, name=None, compare_string=None):
	if None is name:
		name = "plain select"
	# potentially here check the qvars all reference the same input sequence as
	# each other and same for the kvars, technically dont *have* to but is
	# helpful for the user so consider maybe adding a tiny bit of mess here
	# (including markings inside sequences and selectors so they know which
	# index they're gathering to and from) to allow it
	
	# we're ok with getting a single q or k var, not in a tuple,
	# but important to fix it before '+' on two UnfinishedSequences
	# (as opposed to two tuples) sends everything sideways
	q_vars = tupleise(q_vars)
	k_vars = tupleise(k_vars)
	
	# attn layer is one after values it needs to be calculated
	new_depth = _min_poss_depth(q_vars+k_vars)+1
	res = UnfinishedSelect((_input,  # need input seq length to create select
							# of correct size
							UnfinishedSequencesTuple(q_vars),
							UnfinishedSequencesTuple(k_vars)),
						   lambda input_seq, qv, kv: _select(
							   len(input_seq), qv, kv, selector),
						   name=name, compare_string=compare_string,
						   min_poss_depth=new_depth, q_vars=q_vars,
						   k_vars=k_vars, orig_selector=selector)
	return res


def _compose_selects(select1, select2, compose_op=None, name=None,
					 compare_string=None):
	nq1 = len(select1.q_vars)
	nq2 = len(select2.q_vars)+nq1
	nk1 = len(select1.k_vars)+nq2

	def new_selector(*qqkk):
		q1 = qqkk[:nq1]
		q2 = qqkk[nq1:nq2]
		k1 = qqkk[nq2:nk1]
		k2 = qqkk[nk1:]
		return compose_op(select1.orig_selector(*q1, *k1),
						  select2.orig_selector(*q2, *k2))
	return select(select1.q_vars+select2.q_vars,
				  select1.k_vars+select2.k_vars,
				  new_selector, name=name, compare_string=compare_string)


def _compose_select(select1, compose_op=None, name=None, compare_string=None):
	def new_selector(*qk):
		return compose_op(select1.orig_selector(*qk))
	return select(select1.q_vars,
				  select1.k_vars,
				  new_selector, name=name, compare_string=compare_string)


def not_select(select, name=None, compare_string=None):
	return _compose_select(select, lambda a: not a,
						   name=name, compare_string=compare_string)


def and_selects(select1, select2, name=None, compare_string=None):
	return _compose_selects(select1, select2, lambda a, b: a and b,
							name=name, compare_string=compare_string)


def or_selects(select1, select2, name=None, compare_string=None):
	return _compose_selects(select1, select2, lambda a, b: a or b,
							name=name, compare_string=compare_string)


def format_output(parents_tuple, parents2res, name, elementwise_function=None,
				  default=None, min_poss_depth=0, from_zipmap=False,
				  definitely_uses_identity_function=False):
	def_uses = definitely_uses_identity_function
	return UnfinishedSequence(parents_tuple, parents2res,
							  elementwise_function=elementwise_function,
							  default=default, name=name,
							  min_poss_depth=min_poss_depth,
							  from_zipmap=from_zipmap,
							  definitely_uses_identity_function=def_uses)


def get_identity_function(num_params):
	def identity1(a):
		return a

	def identityx(*a):
		return a
	return identity1 if num_params == 1 else identityx


def zipmap(sequences_tuple, elementwise_function,
		   name=plain_unfinished_sequence_name):
	sequences_tuple = tupleise(sequences_tuple)
	unfinished_parents_tuple = UnfinishedSequencesTuple(
		sequences_tuple)  # this also takes care of turning the
	# value in sequences_tuple to indeed a tuple of sequences and not eg a
	# single sequence which will cause weird behaviour later

	parents_tuple = (_input, unfinished_parents_tuple)
	def parents2res(w, vt): return _zipmap(len(w), vt, elementwise_function)
	# feedforward doesn't increase layer
	min_poss_depth = _min_poss_depth(sequences_tuple)
	# new assumption, to be revised later: can do arbitrary zipmap even before
	# first feed-forward, i.e. in build up to first attention. truth is can do
	# 'simple' zipmap towards first attention (no xor, but yes things like
	# 'and' or 'indicator for ==' or whatever) based on initial linear
	# translation done for Q,K in attention (not deep enough for xor, but deep
	# enough for simple stuff) alongside use of initial embedding. honestly
	# literally can just put everything in initial embedding if need it so bad
	# its the first layer and its zipmap its only a function of the token and
	# indices, so long as its not computing any weird combination between them
	# you can do it in the embedding
	# if len(sequences_tuple)>0:
	# 	min_poss_depth = max(min_poss_depth,1) # except for the very specific
	#	# case where it is the very first thing to be done, in which case we do
	#	# have to go through one layer to get to the first feedforward.
	#	# the 'if' is there to rule out increasing when doing a feedforward on
	#	# nothing, ie, when making a constant. constants are allowed to be
	#	# created on layer 0, they're part of the embedding or the weights that
	#	# will use them later or whatever, it's fine
	
	# at least as deep as needed MVs, but no deeper cause FF
	# (which happens at end of layer)
	return format_output(parents_tuple, parents2res, name,
						 min_poss_depth=min_poss_depth,
						 elementwise_function=elementwise_function,
						 from_zipmap=True)  


def aggregate(select, sequences_tuple, elementwise_function=None,
			  default=None, name=plain_unfinished_sequence_name):
	sequences_tuple = tupleise(sequences_tuple)
	definitely_uses_identity_function = None is elementwise_function
	if definitely_uses_identity_function:
		elementwise_function = get_identity_function(len(sequences_tuple))
	unfinished_parents_tuple = UnfinishedSequencesTuple(sequences_tuple)
	parents_tuple = (select, unfinished_parents_tuple)
	def parents2res(s, vt): return _aggregate(
		s, vt, elementwise_function, default=default)
	def_uses = definitely_uses_identity_function
	
	# at least as deep as needed attention and at least one deeper than needed
	# MVs
	return format_output(parents_tuple, parents2res, name,
						 elementwise_function=elementwise_function,
						 default=default,
						 min_poss_depth=max(_min_poss_depth(
							 sequences_tuple)+1, select.min_poss_depth),
						 definitely_uses_identity_function=def_uses)
	

# up to here was just plain transformer 'assembly'. any addition is a lie
# now begin the bells and whistles


def UnfinishedSequenceFunc(f):
	setattr(UnfinishedSequence, f.__name__, f)


def UnfinishedFunc(f):
	setattr(Unfinished, f.__name__, f)


@UnfinishedSequenceFunc
def allow_suppressing_display(self):
	self.always_display = False
	return self  # return self to allow chaining with other calls and throwing
	# straight into a return statement etc

# later, we will overload == for unfinished sequences, such that it always
# returns another unfinished sequence. unfortunately this creates the following
# upsetting behaviour:
# "a in l" and "a==b" always evaluates to true for any unfinishedsequences a,b
# and non-empty list l, and any item a and list l containing at least one
# unfinished sequence. hence, to check if a sequence is really in a list we
# have to do it ourselves, some other way.


def guarded_compare(seq1, seq2):
	if isinstance(seq1, UnfinishedSequence) \
			or isinstance(seq2, UnfinishedSequence):
		return seq1 is seq2
	return seq1 == seq2


def guarded_contains(l, a):
	if isinstance(a, Unfinished):
		return True in [(a is e) for e in l]
	else:
		l = [e for e in l if not isinstance(e, Unfinished)]
		return a in l

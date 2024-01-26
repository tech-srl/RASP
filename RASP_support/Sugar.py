from FunctionalSupport import Unfinished as _Unfinished
from FunctionalSupport import UnfinishedSequence as _UnfinishedSequence
from FunctionalSupport import select, zipmap
from make_operators import add_ops
import DrawCompFlow
# DrawCompFlow is not at all necessary for sugar, but sugar is really the
# top-level rasp file we import, and nice to have draw_comp_flow added into
# the sequences already on load


def _apply_unary_op(self, f):
	return zipmap(self, f)


def _apply_binary_op(self, other, f):
	def seq_and_other_op(self, other, f):
		return zipmap(self, lambda a: f(a, other))

	def seq_and_seq_op(self, other_seq, f):
		return zipmap((self, other_seq), f)
	if isinstance(other, _UnfinishedSequence):
		return seq_and_seq_op(self, other, f)
	else:
		return seq_and_other_op(self, other, f)


add_ops(_UnfinishedSequence, _apply_unary_op, _apply_binary_op)


def _addname(seq, name, default_name, always_display_when_named=True):
	if name is None:
		res = seq.setname(default_name,
						  always_display_when_named=always_display_when_named)
		res = res.allow_suppressing_display()
	else:
		res = seq.setname(name,
						  always_display_when_named=always_display_when_named)
	return res


full_s = select((), (), lambda: True, name="full average",
				compare_string="full average")


def tplconst(v, name=None):
	return _addname(zipmap((), lambda: v), name, "constant: " + str(v),
					always_display_when_named=False).mark_as_constant()
	# always_display_when_named = False : constants aren't worth displaying,
	# but still going to name them in background, in case I change my mind

# allow suppressing display for bool, not, and, or : all of these would have
# been boring operators if only python let me overload them

# always have to call allow_suppressing_display after setname because setname
# marks the variable as crucial to display under assumption user named it


def toseq(seq):
	if not isinstance(seq, _UnfinishedSequence):
		seq = tplconst(seq, str(seq))
	return seq


def asbool(seq):
	res = zipmap(seq, lambda a: bool(a))
	return _addname(res, None, "bool(" + seq.name + ")")
	# would do res = seq==True but it seems this has different behaviour to
	# bool eg 'bool(2)' is True but '2==True' returns False


def tplnot(seq, name=None):
	# this one does correct conversion using asbool and then we really can just
	# do ==False
	res = asbool(seq) == False
	return _addname(res, name, "( not " + str(seq.name) + " )")


def _num_trues(left, right):
	l, r = toseq(left), toseq(right)
	return (1 * asbool(l)) + (1 * asbool(r))


def quickname(v):
	if isinstance(v, _Unfinished):
		return v.name
	else:
		return str(v)


def tpland(left, right):
	res = _num_trues(left, right) == 2
	return _addname(res, None, "( " + quickname(left) + " and "
					+ quickname(right) + ")")


def tplor(left, right):
	res = _num_trues(left, right) >= 1
	return _addname(res, None, "( " + quickname(left) + " or "
					+ quickname(right) + ")")

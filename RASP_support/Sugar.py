from FunctionalSupport import indices, tokens_str, tokens_int, tokens_float, tokens_asis, \
tokens_bool, or_selects, and_selects, not_select
from FunctionalSupport import select, aggregate, zipmap
from FunctionalSupport import UnfinishedSequence as _UnfinishedSequence, Unfinished as _Unfinished
from FunctionalSupport import guarded_compare as _guarded_compare
from FunctionalSupport import guarded_contains as _guarded_contains
import DrawCompFlow # not at all necessary for sugar, but sugar is really the top-level tpl file we import, 
# and nice to have draw_comp_flow added into the sequences already on load
from collections.abc import Iterable
from make_operators import add_ops

def _apply_unary_op(self,f):
	return zipmap(self,f)

def _apply_binary_op(self,other,f):
	def seq_and_other_op(self,other,f):
		return zipmap(self,lambda a:f(a,other))
	def seq_and_seq_op(self,other_seq,f):
		return zipmap((self,other_seq),f)
	if isinstance(other,_UnfinishedSequence):
		return seq_and_seq_op(self,other,f)
	else:
		return seq_and_other_op(self,other,f)

add_ops(_UnfinishedSequence,_apply_unary_op,_apply_binary_op) 


def _addname(seq,name,default_name,always_display_when_named=True):
	if None is name:
		res = seq.setname(default_name,always_display_when_named=always_display_when_named).allow_suppressing_display()
	else:
		res = seq.setname(name,always_display_when_named=always_display_when_named)
	return res


full_s = select((),(),lambda :True,name="full average",compare_string="full average")

def tplconst(v,name=None):
	return _addname(zipmap((),lambda :v),name,"constant: "+str(v),always_display_when_named=False).mark_as_constant()
	# always_display_when_named = False : constants aren't worth displaying, but still going to name them in background,
	# in case change mind about this 

# allow suppressing display for bool, not, and, or : all of these would have been boring operators if
# only python let me overload them

# always have to call allow_suppressing_display after setname because setname marks the variable as
# crucial to display under assumption user named it

def toseq(seq):
	if not isinstance(seq,_UnfinishedSequence):
		seq = tplconst(seq,str(seq))
	return seq

def asbool(seq):
	res = zipmap(seq,lambda a:bool(a))
	return _addname(res,None,"bool("+seq.name+")")
	# would do res = seq==True but it seems this has different behaviour to bool eg 'bool(2)' 
	# is True but '2==True' returns False

def tplnot(seq,name=None):
	res = asbool(seq) == False # this one does correct conversion using asbool and then we really can just do ==False
	return _addname(res,name,"( not "+str(seq.name)+" )")

def _num_trues(l,r):
	l,r = toseq(l),toseq(r)
	return (1*asbool(l)) + (1*asbool(r))

def quickname(v):
	if isinstance(v,_Unfinished):
		return v.name
	else:
		return str(v)

def tpland(l,r):
	res = _num_trues(l,r) == 2
	return _addname(res,None,"( "+quickname(l)+" and "+quickname(r)+")")

def tplor(l,r):
	res = _num_trues(l,r) >= 1
	return _addname(res,None,"( "+quickname(l)+" or "+quickname(r)+")")

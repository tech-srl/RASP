from FunctionalSupport import indices, tokens_str, tokens_int, tokens_float, tokens_asis, \
tokens_bool, or_selects, and_selects, not_select
from FunctionalSupport import select, aggregate, zipmap
from FunctionalSupport import UnfinishedSequence as _UnfinishedSequence
from FunctionalSupport import guarded_compare as _guarded_compare
from FunctionalSupport import guarded_contains as _guarded_contains
import DrawCompFlow # not at all necessary for sugar, but sugar is really the top-level tpl file we import, 
# and nice to have draw_comp_flow added into the sequences already on load
from collections.abc import Iterable
from make_operators import add_ops

def select_i(q_vars,f_get_index,name=None,compare_string=None):
	return select(q_vars,indices,lambda *a:a[-1]==f_get_index(*(a[:-1])))

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


def _seqname(seq):
	def __seqname(seq):
		return getattr(seq,"name",str(seq))
	return __seqname(seq) if not isinstance(seq,Iterable) else "("+", ".join(_seqname(m) for m in seq)+")"

def _tupleise(seqs):
	return tuple(seqs) if isinstance(seqs,Iterable) else (seqs,)

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

def fixorder(seq1,seq2):
	if isinstance(seq1,_UnfinishedSequence):
		return seq1,seq2
	else:
		return seq2,seq1

def tplmax(seq1,seq2,name=None):
	seq1,seq2 = fixorder(seq1,seq2) # order doesnt matter in max, but need to have a sequence on left for _apply_binary_op
	return _addname( _apply_binary_op(seq1,seq2,lambda x,y:max(x,y)),name,
								"max("+_seqname(seq1)+", "+_seqname(seq2)+")")

def tplmin(seq1,seq2,name=None):
	seq1,seq2 = fixorder(seq1,seq2) # order doesnt matter in min, but need to have a sequence on left for _apply_binary_op
	return _addname( _apply_binary_op(seq1,seq2,lambda x,y:min(x,y)),name,
								"min("+_seqname(seq1)+", "+_seqname(seq2)+")")

def average(seqs,f,name=None):
	return _addname(aggregate(full_s,seqs,f),name,"full average")

def frac_quality(seqs,f,name=None,allow_suppressing_display=False):
	if None is name:
		name = "(#quality)/length"
	res = average(seqs,lambda *x:int(f(*x)),name=name)
	if allow_suppressing_display:
		res.always_display = False
	return res

def frac(seq,t,name=None):
	return _addname(average(seq,lambda v:int(v==t)),name,
				"(#"+str(t)+")/length")

length = round(1/frac(indices,0)).setname("length")
flip_s = select_i((indices,length),lambda i,n:n-(i+1),
					name="flip select",compare_string="full flip")

# allow suppressing display for bool, not, and, or : all of these would have been boring operators if
# only python let me overload them

# always have to call allow_suppressing_display after setname because setname marks the variable as
# crucial to display under assumption user named it

def toseq(seq):
	if not isinstance(seq,_UnfinishedSequence):
		seq = tplconst(seq,str(seq))
	return seq

def asbool(seq,name=None):
	res = zipmap(seq,lambda a:bool(a))
	return _addname(res,name,"bool("+seq.name+")")
	# would do res = seq==True but it seems this has different behaviour to bool eg 'bool(2)' 
	# is True but '2==True' returns False

def asint(seq,name=None):
	res = zipmap(seq,lambda a:int(a))
	return _addname(res,name,"int("+seq.name+")")
	# would do res = seq==True but it seems this has different behaviour to bool eg 'bool(2)' 
	# is True but '2==True' returns False

def tplnot(seq,name=None):
	res = asbool(seq) == False # this one does correct conversion using asbool and then we really can just do ==False
	return _addname(res,name,"( not "+str(seq.name)+" )")

def count_trues_across_vars(*seqs,name=None):
	res = asbool(seqs[0])*1
	for seq in seqs[1:]:
		res += 1*asbool(seq)
	return _addname(res,name,"num trues")

def tpland(*seqs,name=None):
	seqs = tuple(toseq(s) for s in seqs)
	res = count_trues_across_vars(*seqs) == len(seqs)
	return _addname(res,name,"( "+" and ".join(seq.name for seq in seqs)+")")

def tplor(*seqs,name=None):
	seqs = tuple(toseq(s) for s in seqs)
	res = count_trues_across_vars(*seqs) > 0
	return _addname(res,name,"( "+" or ".join(seq.name for seq in seqs)+")")

def tplxor(seq1,seq2,name=None):
	res = tplor( tpland(seq1,tplnot(seq2)) , tpland(tplnot(seq1),seq2) )
	return _addname(res,name,"( "+seq1.name+" xor "+seq2.name+" )")

def conditioned_contains(qseqs,kseqs,f,name=None,allow_suppressing_display=False,sel_name=None):
	if None is name:
		name = "conditioned contains"
	s = select(qseqs,kseqs,f,name=sel_name)
	res = aggregate(s,(),lambda :1,default=0,name=name+" (as number)") > 0
	res.setname(name)
	if allow_suppressing_display:
		res.allow_suppressing_display()
	return res

def count_conditioned(qseqs,kseqs,f,name=None):
	# output 1 at 0th index and 0 everywhere else
	# focus on 0th index and on all hits
	# obtained fraction helps deduce how many hits you had except for 0th index
	# add 1/0 depending on whether 0 is a hit
	if not isinstance(kseqs,Iterable):
		kseqs = (kseqs,)
	kseqs = kseqs + (indices,)
	s = select(qseqs,kseqs,lambda *a:f(*(a[:-1])) or (a[-1]==0),name="find all conditions, and 0.")
	frac = aggregate(s,indices,lambda i:int(i==0), 
				name="1/(1+(n outside 0)), for "+(name if not None is name else "condition"))
	count_outside_0 = (1/frac)-1
	count_outside_0.setname("count outside 0")
	contains_in_0 = conditioned_contains(qseqs,kseqs,lambda *a:f(*(a[:-1])) and (a[-1]==0),
										name="check 0, for "+(name if not None is name else "condition"),
										allow_suppressing_display=True,sel_name="find condition, but only at 0")
	contains_in_0.setname("count at 0")
	res = count_outside_0 + contains_in_0
	if None is name:
		name = "count conditioned"
	return res.setname(name).allow_suppressing_display() # if goes straight into something else

def contains_quality(seqs,f,name=None):
	if None is name:
		name = "contains quality"
	return conditioned_contains((),seqs,f,name=name)

def contains(seq,t,name=None):
	if None is name:
		name = "contains "+str(t)
	return contains_quality(seq,lambda v:v==t,name=name)

def count_quality(seqs,f,name=None,allow_suppressing_display=False):
	if None is name:
		name = "count of quality"
	res = round( frac_quality(seqs,f,allow_suppressing_display=True) * length )
	res.setname(name)
	if allow_suppressing_display:
		res.allow_suppressing_display()
	return res

def count(seq,t,name=None):
	if None is name:
		name = "count "+str(t)
	return count_quality(seq,lambda v:v==t,name=name)

def shift_select(n):
	# plain! selects from global indices
	return select_i(indices,lambda i:i+n,name="shift "+str(n),
					compare_string="full shift by "+str(n))

def index_select(i): 
	# plain! selects from global indices
	name="select index "+str(i)
	compare_string="full index seek ("+str(i)+")"
	if i<0:
		locseq = length+i
		return select_i(locseq,lambda a:a,name=name,compare_string=compare_string)
	else:
		return select_i((),lambda :i,name=name,compare_string=compare_string) 



def load_from_target_index(i,seq,default,name=None): # can probably do a getitem overload for this, if not too confusing..
	if None is name:
		name = seq.name+"["+str(i)+"]"
	return aggregate(index_select(i),seq,default=default,name=name)

def load_from_target_indices(locseq,seq,default,name=None):
	assert not isinstance(locseq,Iterable) and not isinstance(seq,Iterable)
	s = select_i(locseq,lambda a:a,compare_string="load from indices given by seq #"+str(locseq.creation_order_id))
	return aggregate(s,seq,default=default,name=name)

def item_select(seq,val,name=None): 
	if None is name:
		name = "focus on "+seq.name
	return select((),seq,lambda v:v==val,"full seek of ["+repr(val)+"] in seq #"+str(seq.creation_order_id))

def get_shifted(seq,n,filler,name=None):
	assert not isinstance(seq,Iterable) # just want the one here, makes more sense or maybe just am lazy
	if None is name:
		name = str(n)+"-shifted "+seq.name
	return aggregate(shift_select(n),seq,default=filler,name=name)
	
def mark_last_condition(seqs,f,name=None): 
	if None is name:
		name = "last to satisfy f"
	if not isinstance(seqs,Iterable): # just one seq
		seqs = (seqs,)
	satisfies_f = zipmap(seqs,f,name="satisfies f").allow_suppressing_display()
	has_later = conditioned_contains(indices,(satisfies_f,indices),lambda i,sf,j:sf and (i<j),name="exists later satisfying f").allow_suppressing_display()
	return tpland(satisfies_f,tplnot(has_later),name=name) # the fact that we have given it a name will prevent suppression in display

def mark_first_condition(seqs,f,name=None):
	if None is name:
		name = "first to satisfy f"
	if not isinstance(seqs,Iterable): # just one seq
		seqs = (seqs,)
	satisfies_f = zipmap(seqs,f,name="satisfies f").allow_suppressing_display()
	has_earlier = conditioned_contains(indices,(satisfies_f,indices),lambda i,sf,j:sf and (i>j),name="exists earlier satisfying f").allow_suppressing_display()
	return tpland(satisfies_f,tplnot(has_earlier),name=name) # the fact that we have given it a name will prevent suppression in display

def mark_last_value(seq,v,name=None):
	if None is name:
		name = "last "+str(v)+" in "+seq.name
	return mark_last_condition(seq,lambda e:e==v,name=name)

def mark_first_value(seq,v,name=None):
	if None is name:
		name = "first "+str(v)+" in "+seq.name
	return mark_first_condition(seq,lambda e:e==v,name=name)

# def find_last_instance(seq,v,name=None):
# 	if None is name:
# 		name = "index of last instance of "+str(v)
# 	return find_last_condition(seq,lambda e:e==v,name=name)

def select_from_last_condition(k_vars,f,name=None): # todo: generalise to select from i'th condition, with i's both positive and negative
	# will write everywhere, but read only from k_vars
	if None is name:
		name = "select last satisfying f from k_vars"
	return select((),mark_last_condition(k_vars,f).allow_suppressing_display(),
									lambda a:a,name=name)

def select_from_first_condition(k_vars,f,name=None): # todo: generalise to select from i'th condition, with i's both positive and negative
	# will write everywhere, but read only from k_vars
	if None is name:
		name = "select first satisfying f from k_vars"
	return select((),mark_first_condition(k_vars,f).allow_suppressing_display(),
									lambda a:a,name=name)

def select_from_last_value(k_var,v,name=None):
	# will write everywhere, but read only from k_vars
	if None is name:
		name = "select last "+str(v)
	assert not isinstance(k_var,Iterable), "got iterable k vars in select last "+str(v)+" in "+k_var.name
	return select_from_last_condition(k_var,lambda e:e==v,name=name)

def select_from_first_value(k_var,v,name=None):
	# will write everywhere, but read only from k_vars
	if None is name:
		name = "select first "+str(v)
	assert not isinstance(k_var,Iterable), "got iterable k vars in select last "+str(v)+" in "+k_var.name
	return select_from_first_condition(k_var,lambda e:e==v,name=name)

def sort(seqs,key=None,name=None):
	keyname = "" if None is key else ", key="+_seqname(key)
	if None is key:
		assert not isinstance(seqs,Iterable)
		key = seqs
	num_smaller = count_conditioned((key,indices),(key,indices),
							lambda vq,iq,vk,ik:(vk<vq) or ((vk==vq and ik<iq)),name="num smaller")
	focus_on_new_self = select(indices,num_smaller,lambda i,n:i==n,"focus on new value")
	if None is name:
		name = "sorted("+_seqname(seqs)+keyname+")"
	return aggregate(focus_on_new_self,seqs,name=name)

def select_next_equal(seq): 
	num_prev = count_conditioned((seq,indices),(seq,indices),lambda qt,qi,kt,ki:(qt==kt) and (ki<qi))
	sel_next = select((seq,num_prev),(seq,num_prev),lambda qt,qp,kt,kp:(qt==kt) and (qp+1==kp))
	return sel_next


# extend UnfinishedSequence with a bunch of operators,
# provided the unary and binary ops.
# make them fully named functions instead of lambdas, even though
# it's more lines, because the debug prints are so much clearer
# this way
def add_ops(Class, apply_unary_op, apply_binary_op):

	def addsetname(f, opname, rev):
		def f_with_setname(*a):

			assert len(a) in [1, 2]
			if len(a) == 2:
				a0, a1 = a if not rev else (a[1], a[0])
				name0 = a0.name if hasattr(a0, "name") else str(a0)
				name1 = a1.name if hasattr(a1, "name") else str(a1)
				# a0/a1 might not be a seq, just having an op on it with a seq.
				name = name0 + " " + opname + " " + name1
			else:  # len(a)==1
				name = opname + " " + a[0].name
			# probably going to be composed with more ops, so...
			name = "( " + name + " )"
			return f(*a).setname(name).allow_suppressing_display()
			# seqs created as parts of long sequences of operators may be
			# suppressed in display, the final name of the whole composition
			# will be sufficiently informative. Have to set always_display to
			# false *after* the setname, because setname marks always_display
			# as True (under assumption it is normally being called by the
			# user, who must clearly be naming some variable they care about)
		return f_with_setname

	def listop(f, listing_name):
		setattr(Class, listing_name, f)

	def addop(opname, rev=False):
		return lambda f: listop(addsetname(f, opname, rev), f.__name__)

	@addop("==")
	def __eq__(self, other):
		return apply_binary_op(self, other, lambda a, b: a == b)

	@addop("!=")
	def __ne__(self, other):
		return apply_binary_op(self, other, lambda a, b: a != b)

	@addop("<")
	def __lt__(self, other):
		return apply_binary_op(self, other, lambda a, b: a < b)

	@addop(">")
	def __gt__(self, other):
		return apply_binary_op(self, other, lambda a, b: a > b)

	@addop("<=")
	def __le__(self, other):
		return apply_binary_op(self, other, lambda a, b: a <= b)

	@addop(">=")
	def __ge__(self, other):
		return apply_binary_op(self, other, lambda a, b: a >= b)

	@addop("+")
	def __add__(self, other):
		return apply_binary_op(self, other, lambda a, b: a+b)

	@addop("+", True)
	def __radd__(self, other):
		return apply_binary_op(self, other, lambda a, b: b+a)

	@addop("-")
	def __sub__(self, other):
		return apply_binary_op(self, other, lambda a, b: a-b)

	@addop("-", True)
	def __rsub__(self, other):
		return apply_binary_op(self, other, lambda a, b: b-a)

	@addop("*")
	def __mul__(self, other):
		return apply_binary_op(self, other, lambda a, b: a*b)

	@addop("*", True)
	def __rmul__(self, other):
		return apply_binary_op(self, other, lambda a, b: b*a)

	@addop("//")
	def __floordiv__(self, other):
		return apply_binary_op(self, other, lambda a, b: a//b)

	@addop("//", True)
	def __rfloordiv__(self, other):
		return apply_binary_op(self, other, lambda a, b: b//a)

	@addop("/")
	def __truediv__(self, other):
		return apply_binary_op(self, other, lambda a, b: a/b)

	@addop("/", True)
	def __rtruediv__(self, other):
		return apply_binary_op(self, other, lambda a, b: b/a)

	@addop("%")
	def __mod__(self, other):
		return apply_binary_op(self, other, lambda a, b: a % b)

	@addop("%", True)
	def __rmod__(self, other):
		return apply_binary_op(self, other, lambda a, b: b % a)

	@addop("divmod")
	def __divmod__(self, other):
		return apply_binary_op(self, other, lambda a, b: divmod(a, b))

	@addop("divmod", True)
	def __rdivmod__(self, other):
		return apply_binary_op(self, other, lambda a, b: divmod(b, a))

	@addop("pow")
	def __pow__(self, other):
		return apply_binary_op(self, other, lambda a, b: pow(a, b))

	@addop("pow", True)
	def __rpow__(self, other):
		return apply_binary_op(self, other, lambda a, b: pow(b, a))

	# skipping and, or, xor, which are bitwise and dont implement 'and' and
	# 'or' but rather & and | similarly skipping lshift, rshift cause who wants
	# them wish i had not, and, or primitives, but can accept that dont.
	# if people really want to do 'not' they can do '==False' instead, can do a
	# little macro for it in the other sugar file or whatever

	@addop("+")
	def __pos__(self):
		return apply_unary_op(self, lambda a: +a)

	@addop("-")
	def __neg__(self):
		return apply_unary_op(self, lambda a: -a)

	@addop("abs")
	def __abs__(self):
		return apply_unary_op(self, abs)

	@addop("round")
	# not sure if python will get upset if round doesnt return an actual int
	# tbh... will have to check.
	def __round__(self):
		return apply_unary_op(self, round)

	# defining floor, ceil, trunc showed up funny (green instead of blue),
	# gonna go ahead and avoid

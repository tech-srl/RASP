# Generated from RASP.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
	from .RASPParser import RASPParser
else:
	from RASPParser import RASPParser

# This class defines a complete generic visitor for a parse tree produced by RASPParser.

class RASPVisitor(ParseTreeVisitor):

	# Visit a parse tree produced by RASPParser#r.
	def visitR(self, ctx:RASPParser.RContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#statement.
	def visitStatement(self, ctx:RASPParser.StatementContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#raspstatement.
	def visitRaspstatement(self, ctx:RASPParser.RaspstatementContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#replstatement.
	def visitReplstatement(self, ctx:RASPParser.ReplstatementContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#setExample.
	def visitSetExample(self, ctx:RASPParser.SetExampleContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#showExample.
	def visitShowExample(self, ctx:RASPParser.ShowExampleContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#toggleSeqVerbose.
	def visitToggleSeqVerbose(self, ctx:RASPParser.ToggleSeqVerboseContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#toggleExample.
	def visitToggleExample(self, ctx:RASPParser.ToggleExampleContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#exit.
	def visitExit(self, ctx:RASPParser.ExitContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#loadFile.
	def visitLoadFile(self, ctx:RASPParser.LoadFileContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#assign.
	def visitAssign(self, ctx:RASPParser.AssignContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#draw.
	def visitDraw(self, ctx:RASPParser.DrawContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#exprsList.
	def visitExprsList(self, ctx:RASPParser.ExprsListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#namedExprsList.
	def visitNamedExprsList(self, ctx:RASPParser.NamedExprsListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#namedExpr.
	def visitNamedExpr(self, ctx:RASPParser.NamedExprContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#raspstatementsList.
	def visitRaspstatementsList(self, ctx:RASPParser.RaspstatementsListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#funcDef.
	def visitFuncDef(self, ctx:RASPParser.FuncDefContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#forLoop.
	def visitForLoop(self, ctx:RASPParser.ForLoopContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#commentsList.
	def visitCommentsList(self, ctx:RASPParser.CommentsListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#assignsAndCommentsList.
	def visitAssignsAndCommentsList(self, ctx:RASPParser.AssignsAndCommentsListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#returnStatement.
	def visitReturnStatement(self, ctx:RASPParser.ReturnStatementContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#idsList.
	def visitIdsList(self, ctx:RASPParser.IdsListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#aggregateExpr.
	def visitAggregateExpr(self, ctx:RASPParser.AggregateExprContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#atom.
	def visitAtom(self, ctx:RASPParser.AtomContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#expr.
	def visitExpr(self, ctx:RASPParser.ExprContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#aList.
	def visitAList(self, ctx:RASPParser.AListContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#aDict.
	def visitADict(self, ctx:RASPParser.ADictContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#listCompExpr.
	def visitListCompExpr(self, ctx:RASPParser.ListCompExprContext):
		return self.visitChildren(ctx)


	# Visit a parse tree produced by RASPParser#dictCompExpr.
	def visitDictCompExpr(self, ctx:RASPParser.DictCompExprContext):
		return self.visitChildren(ctx)



del RASPParser

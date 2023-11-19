# Generated from RASP.g4 by ANTLR 4.9
from antlr4 import *
if __name__ is not None and "." in __name__:
	from .RASPParser import RASPParser
else:
	from RASPParser import RASPParser

# This class defines a complete listener for a parse tree produced by RASPParser.
class RASPListener(ParseTreeListener):

	# Enter a parse tree produced by RASPParser#r.
	def enterR(self, ctx:RASPParser.RContext):
		pass

	# Exit a parse tree produced by RASPParser#r.
	def exitR(self, ctx:RASPParser.RContext):
		pass


	# Enter a parse tree produced by RASPParser#statement.
	def enterStatement(self, ctx:RASPParser.StatementContext):
		pass

	# Exit a parse tree produced by RASPParser#statement.
	def exitStatement(self, ctx:RASPParser.StatementContext):
		pass


	# Enter a parse tree produced by RASPParser#raspstatement.
	def enterRaspstatement(self, ctx:RASPParser.RaspstatementContext):
		pass

	# Exit a parse tree produced by RASPParser#raspstatement.
	def exitRaspstatement(self, ctx:RASPParser.RaspstatementContext):
		pass


	# Enter a parse tree produced by RASPParser#replstatement.
	def enterReplstatement(self, ctx:RASPParser.ReplstatementContext):
		pass

	# Exit a parse tree produced by RASPParser#replstatement.
	def exitReplstatement(self, ctx:RASPParser.ReplstatementContext):
		pass


	# Enter a parse tree produced by RASPParser#setExample.
	def enterSetExample(self, ctx:RASPParser.SetExampleContext):
		pass

	# Exit a parse tree produced by RASPParser#setExample.
	def exitSetExample(self, ctx:RASPParser.SetExampleContext):
		pass


	# Enter a parse tree produced by RASPParser#showExample.
	def enterShowExample(self, ctx:RASPParser.ShowExampleContext):
		pass

	# Exit a parse tree produced by RASPParser#showExample.
	def exitShowExample(self, ctx:RASPParser.ShowExampleContext):
		pass


	# Enter a parse tree produced by RASPParser#toggleSeqVerbose.
	def enterToggleSeqVerbose(self, ctx:RASPParser.ToggleSeqVerboseContext):
		pass

	# Exit a parse tree produced by RASPParser#toggleSeqVerbose.
	def exitToggleSeqVerbose(self, ctx:RASPParser.ToggleSeqVerboseContext):
		pass


	# Enter a parse tree produced by RASPParser#toggleExample.
	def enterToggleExample(self, ctx:RASPParser.ToggleExampleContext):
		pass

	# Exit a parse tree produced by RASPParser#toggleExample.
	def exitToggleExample(self, ctx:RASPParser.ToggleExampleContext):
		pass


	# Enter a parse tree produced by RASPParser#exit.
	def enterExit(self, ctx:RASPParser.ExitContext):
		pass

	# Exit a parse tree produced by RASPParser#exit.
	def exitExit(self, ctx:RASPParser.ExitContext):
		pass


	# Enter a parse tree produced by RASPParser#loadFile.
	def enterLoadFile(self, ctx:RASPParser.LoadFileContext):
		pass

	# Exit a parse tree produced by RASPParser#loadFile.
	def exitLoadFile(self, ctx:RASPParser.LoadFileContext):
		pass


	# Enter a parse tree produced by RASPParser#assign.
	def enterAssign(self, ctx:RASPParser.AssignContext):
		pass

	# Exit a parse tree produced by RASPParser#assign.
	def exitAssign(self, ctx:RASPParser.AssignContext):
		pass


	# Enter a parse tree produced by RASPParser#draw.
	def enterDraw(self, ctx:RASPParser.DrawContext):
		pass

	# Exit a parse tree produced by RASPParser#draw.
	def exitDraw(self, ctx:RASPParser.DrawContext):
		pass


	# Enter a parse tree produced by RASPParser#exprsList.
	def enterExprsList(self, ctx:RASPParser.ExprsListContext):
		pass

	# Exit a parse tree produced by RASPParser#exprsList.
	def exitExprsList(self, ctx:RASPParser.ExprsListContext):
		pass


	# Enter a parse tree produced by RASPParser#namedExprsList.
	def enterNamedExprsList(self, ctx:RASPParser.NamedExprsListContext):
		pass

	# Exit a parse tree produced by RASPParser#namedExprsList.
	def exitNamedExprsList(self, ctx:RASPParser.NamedExprsListContext):
		pass


	# Enter a parse tree produced by RASPParser#namedExpr.
	def enterNamedExpr(self, ctx:RASPParser.NamedExprContext):
		pass

	# Exit a parse tree produced by RASPParser#namedExpr.
	def exitNamedExpr(self, ctx:RASPParser.NamedExprContext):
		pass


	# Enter a parse tree produced by RASPParser#raspstatementsList.
	def enterRaspstatementsList(self, ctx:RASPParser.RaspstatementsListContext):
		pass

	# Exit a parse tree produced by RASPParser#raspstatementsList.
	def exitRaspstatementsList(self, ctx:RASPParser.RaspstatementsListContext):
		pass


	# Enter a parse tree produced by RASPParser#funcDef.
	def enterFuncDef(self, ctx:RASPParser.FuncDefContext):
		pass

	# Exit a parse tree produced by RASPParser#funcDef.
	def exitFuncDef(self, ctx:RASPParser.FuncDefContext):
		pass


	# Enter a parse tree produced by RASPParser#forLoop.
	def enterForLoop(self, ctx:RASPParser.ForLoopContext):
		pass

	# Exit a parse tree produced by RASPParser#forLoop.
	def exitForLoop(self, ctx:RASPParser.ForLoopContext):
		pass


	# Enter a parse tree produced by RASPParser#commentsList.
	def enterCommentsList(self, ctx:RASPParser.CommentsListContext):
		pass

	# Exit a parse tree produced by RASPParser#commentsList.
	def exitCommentsList(self, ctx:RASPParser.CommentsListContext):
		pass


	# Enter a parse tree produced by RASPParser#assignsAndCommentsList.
	def enterAssignsAndCommentsList(self, ctx:RASPParser.AssignsAndCommentsListContext):
		pass

	# Exit a parse tree produced by RASPParser#assignsAndCommentsList.
	def exitAssignsAndCommentsList(self, ctx:RASPParser.AssignsAndCommentsListContext):
		pass


	# Enter a parse tree produced by RASPParser#returnStatement.
	def enterReturnStatement(self, ctx:RASPParser.ReturnStatementContext):
		pass

	# Exit a parse tree produced by RASPParser#returnStatement.
	def exitReturnStatement(self, ctx:RASPParser.ReturnStatementContext):
		pass


	# Enter a parse tree produced by RASPParser#idsList.
	def enterIdsList(self, ctx:RASPParser.IdsListContext):
		pass

	# Exit a parse tree produced by RASPParser#idsList.
	def exitIdsList(self, ctx:RASPParser.IdsListContext):
		pass


	# Enter a parse tree produced by RASPParser#aggregateExpr.
	def enterAggregateExpr(self, ctx:RASPParser.AggregateExprContext):
		pass

	# Exit a parse tree produced by RASPParser#aggregateExpr.
	def exitAggregateExpr(self, ctx:RASPParser.AggregateExprContext):
		pass


	# Enter a parse tree produced by RASPParser#atom.
	def enterAtom(self, ctx:RASPParser.AtomContext):
		pass

	# Exit a parse tree produced by RASPParser#atom.
	def exitAtom(self, ctx:RASPParser.AtomContext):
		pass


	# Enter a parse tree produced by RASPParser#expr.
	def enterExpr(self, ctx:RASPParser.ExprContext):
		pass

	# Exit a parse tree produced by RASPParser#expr.
	def exitExpr(self, ctx:RASPParser.ExprContext):
		pass


	# Enter a parse tree produced by RASPParser#aList.
	def enterAList(self, ctx:RASPParser.AListContext):
		pass

	# Exit a parse tree produced by RASPParser#aList.
	def exitAList(self, ctx:RASPParser.AListContext):
		pass


	# Enter a parse tree produced by RASPParser#aDict.
	def enterADict(self, ctx:RASPParser.ADictContext):
		pass

	# Exit a parse tree produced by RASPParser#aDict.
	def exitADict(self, ctx:RASPParser.ADictContext):
		pass


	# Enter a parse tree produced by RASPParser#listCompExpr.
	def enterListCompExpr(self, ctx:RASPParser.ListCompExprContext):
		pass

	# Exit a parse tree produced by RASPParser#listCompExpr.
	def exitListCompExpr(self, ctx:RASPParser.ListCompExprContext):
		pass


	# Enter a parse tree produced by RASPParser#dictCompExpr.
	def enterDictCompExpr(self, ctx:RASPParser.DictCompExprContext):
		pass

	# Exit a parse tree produced by RASPParser#dictCompExpr.
	def exitDictCompExpr(self, ctx:RASPParser.DictCompExprContext):
		pass



del RASPParser

//compile with:
// antlr4 -Dlanguage=Python3 -visitor RASP.g4 -o zzantlr/ 
grammar RASP;
r : (statement)+? EOF ;   
statement : raspstatement Comment? | replstatement Comment? | Comment ;
raspstatement : expr ';' | assign ';' | draw ';' | loadFile ';'| funcDef | forLoop ;
replstatement : setExample | showExample | toggleExample | toggleSeqVerbose | exit ;
setExample : 'set' subset=('s-op'|'selector')? 'example' example=expr ; 
showExample : 'show' subset=('s-op'|'selector')? 'example';
toggleSeqVerbose : 'full seq display' switch=('on'|'off');
toggleExample : subset=('s-op'|'selector')? 'examples' switch=('on'|'off'); 
exit : 'exit()' | 'exit' | 'quit' | 'quit()' ;

loadFile : 'load' filename=String;
assign : var=idsList '=' val=exprsList;
draw : 'draw' '(' unf=expr (',' inputseq=expr)?')';
exprsList : first=expr (',' cont=exprsList)?; 
namedExprsList: first=namedExpr (',' cont=namedExprsList)?;
namedExpr: key=expr ':' val=expr;
raspstatementsList : first=raspstatement Comment? (cont=raspstatementsList)? | Comment (cont=raspstatementsList)? ;
funcDef: 'def' name=ID '(' (arguments=idsList)? ')' '{' 
			commentsList?  (mainbody=raspstatementsList)? //(mainbody=assignsAndCommentsList)? 
			retstatement=returnStatement commentsList? '}';
forLoop: 'for' iterator=idsList 'in' iterable=expr  '{' mainbody=raspstatementsList '}';
commentsList: Comment (cont=commentsList)?;
assignsAndCommentsList : first=assign ';' Comment? (cont=assignsAndCommentsList)? 
						| Comment (cont=assignsAndCommentsList)?;
returnStatement : 'return' res=exprsList ';';
idsList : first=ID (',' cont=idsList)?;
aggregateExpr: 'aggregate(' sel=expr ',' seq=expr (',' default=expr)? ')';
atom : anint=PosInt | afloat=Float | astring=String; 


expr
 : '(' bracketed=expr ')'
 | indexable=expr '[' index=expr ']'  // just fails if bad index
 | unfORfun=expr '(' (inputexprs=exprsList)? ')' // bit problematic cause if unfORfun is an unf 
 												//this is actually not an expression, make sure such cases 
												// get caught and handled properly
 | uop=('not'|'-'|'+') uexpr=expr
 | uop=('round'|'indicator') '(' uexpr=expr ')'
 | left=expr bop='^' right=expr
 | left=expr bop=('*'|'/') right=expr
 | left=expr bop='%' right=expr
 | left=expr bop=('+'|'-') right=expr
 | left=expr bop=('=='|'<='|'>='|'>'|'<') right=expr
 | 'select(' key=expr ','  query=expr ',' selop=('=='|'<'|'>'|'>='|'<='|'!=') ')'
 | left=expr bop=('and'|'or') right=expr
 | res1=expr 'if' cond=expr 'else' res2=expr
 | var=ID 
 | standalone=atom
 | aList | aDict
 | aggregate=aggregateExpr
 | 'range(' rangevals=exprsList ')'
 | listcomp=listCompExpr
 | dictcomp=dictCompExpr
 | contained=expr 'in' container=expr
 | 'zip(' lists=exprsList ')'
 | 'len(' singleList=expr ')'
 ;

aList: '[' listContents=exprsList? ']';
aDict: '{' dictContents=namedExprsList? '}';


listCompExpr : '[' val=expr 'for' iterator=idsList 'in' iterable=expr ']';
dictCompExpr : '{' key=expr ':' val=expr 'for' iterator=idsList 'in' iterable=expr '}';
// negative ints come from the expression expr -> '-' expr -> '-' atom -> '-' PosInt
// bools are stored in the environment as reserved words, don't need to be in the grammar (only 2 vals)
// (recognised by the grammar as an identifier)

Float : PosInt'.'PosInt ;// no fancy floats here sir, this is a simple operation
PosInt : [0-9]+ ;
// CommentContent: ~[\r\n]+ ; // keep going until newline
String: '"' ~["\r\n]* '"';
Comment : '#' ~( '\r' | '\n' )* ;

ID: [a-zA-Z_] [a-zA-Z_0-9]*;
WS : [ \t\r\n]+ -> skip ; // skip spaces, tabs, newlines
// ErrorChars : .+? ; 
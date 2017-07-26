import sys

from keras.models import Sequential
from keras.layers import Dense, Dropout, Input, Embedding, LSTM
from keras.models import Model
from keras import optimizers
from keras.callbacks import ModelCheckpoint, CSVLogger, EarlyStopping
from keras.models import model_from_yaml

from Token import Token
from compile_error import CompileError
import tokenize
import token
import StringIO
import keyword
import json
import numpy as np

global all_tokens
global indexed_tokens

START_TOKEN = '<s>'
END_TOKEN = '</s>'

def one_hot(indexed_tokens):
	one_hot = []
	nb_classes = 88
	one_hot_targets = np.eye(nb_classes)[indexed_tokens]
	one_hot = one_hot_targets.tolist()
	#print "fort"
	#bruhTemp = one_hot[:]
	for x in range(len(one_hot)):
		#one_hot[x].astype(int)
		[int(i) for i in one_hot[x]]
	#one_hot.astype(int)
	#print type(one_hot[0][0])
	return one_hot
	

def set_from_json(all_tokens, flag):
	#print "OMG"
	with open('vocabulary.json') as data_file:    
    		data = json.load(data_file)
		#pprint(data)
	#print len(data["indexes"])
	#print "DHADHA"

	tempT = all_tokens[:]
	for token in tempT:
		if len(token.value) > 0:
			if token.value[0] == '#':
				all_tokens.remove(token)
				#print "no way"

	for token in all_tokens:
		if token.value == "\\r\\n":
			token.value = "NEWLINE"
		toCompare = token.value
		#print token.type
		#print "Broke..."
		#print token.line
		global indexed_tokens
		indexed_tokens.append(data["indexes"].index(toCompare))
	for r in range(9):
		indexed_tokens.insert(r, data["indexes"].index(START_TOKEN))
		indexed_tokens.append(data["indexes"].index(END_TOKEN))
		
	#print indexed_tokens
	return one_hot(indexed_tokens)

def open_closed_tokens(token):
    """
    'Flattens' Python into tokens based on whether the token is open or
    closed.
    """

    # List of token names that whose text should be used verbatim as the type.
    VERBATIM_CLASSES = {
        "AMPER", "AMPEREQUAL", "ASYNC", "AT", "ATEQUAL", "AWAIT", "CIRCUMFLEX",
        "CIRCUMFLEXEQUAL", "COLON", "COMMA", "DOT", "DOUBLESLASH",
        "DOUBLESLASHEQUAL", "DOUBLESTAR", "DOUBLESTAREQUAL", "ELLIPSIS",
        "EQEQUAL", "EQUAL", "GREATER", "GREATEREQUAL", "LBRACE", "LEFTSHIFT",
        "LEFTSHIFTEQUAL", "LESS", "LESSEQUAL", "LPAR", "LSQB", "MINEQUAL",
        "MINUS", "NOTEQUAL", "OP", "PERCENT", "PERCENTEQUAL", "PLUS", "PLUSEQUAL",
        "RARROW", "RBRACE", "RIGHTSHIFT", "RIGHTSHIFTEQUAL", "RPAR", "RSQB",
        "SEMI", "SLASH", "SLASHEQUAL", "STAR", "STAREQUAL", "TILDE", "VBAR",
        "VBAREQUAL"
    }
 
    OTHER = { "NEWLINE", "INDENT", "DEDENT"}
    CHECK = {"None", "True", "False"}

    if token.type == 'NAME':
        # Special case for NAMES, because they can also be keywords.
        if keyword.iskeyword(token.value):
            return token.value
	elif token.value in CHECK:
	    return token.value
        else:
            return '<IDENTIFIER>'
    elif token.type in VERBATIM_CLASSES:
        # These tokens should be mapped verbatim to their names.
        assert ' ' not in token.value
        return token.value
    elif token.type in {'NUMBER', 'STRING'}:
        # These tokens should be abstracted.
        # Use the <ANGLE-BRACKET> notation to signify these classes.        
	return "<" + token.type.upper() + ">"
    elif token.type in OTHER:
        return token.type
    else:
        # Use these token's name verbatim.
       # assert token.type in {
        #    'NEWLINE', 'INDENT', 'DEDENT',
        #    'ENDMARKER', 'ENCODING', 'COMMENT', 'NL', 'ERRORTOKEN'
        #}
	
        return token.value
	
def vocabularize_tokens(every_token, flag):
    if flag == False:
   	 EXTRANEOUS_TOKENS = {
             # Always occurs as the first token: internally indicates the file
             # ecoding, but is irrelelvant once the stream is already tokenized
            'ENCODING',
	
            # Always occurs as the last token.
            'ENDMARKER',

            # Insignificant newline; not to be confused with NEWLINE
            'NL',
	
            # Discard comments
            'COMMENT',

            # Represents a tokenization error. This should never appear for
            # syntatically correct files.
            'ERRORTOKEN',
        }
    elif flag == True:
        EXTRANEOUS_TOKENS = {
             # Always occurs as the first token: internally indicates the file
             # ecoding, but is irrelelvant once the stream is already tokenized
            'ENCODING',
	
            # Always occurs as the last token.
            'ENDMARKER',

            # Discard comments
            'COMMENT',

            # Represents a tokenization error. This should never appear for
            # syntatically correct files.
            'ERRORTOKEN',
        }
    

    
    all_tokens_iter = every_token[:]
    for Token in all_tokens_iter:

       	vocab_entry = open_closed_tokens(Token)
	Token.value = vocab_entry
        if Token.type in EXTRANEOUS_TOKENS:
		every_token.remove(Token)
	if flag == True:
		if Token.value == "\\n":
			every_token.remove(Token)
			#if Token.type == "NL":
			#print "Gotch u"
   
    #for Token in every_token:
    #print Token.value
    return set_from_json(every_token, flag)


# Create list of tokens
def handle_token(type, token, (srow, scol), (erow, ecol), line):
    if repr(token)[:2] == 'u\'':
	val = repr(token)[2:len(repr(token))-1]
    else:
        val = repr(token)[1:len(repr(token))-1]
    send = Token(tokenize.tok_name[type], val, srow, scol, erow, ecol, line)
    global all_tokens
    all_tokens.append(send)
    #print "%d,%d-%d,%d:\t%s\t%s" % \
    #    (srow, scol, erow, ecol, tokenize.tok_name[type], repr(token))

def getFileTokens(fileName):
	with open(fileName, 'r') as myfile:
    		data=myfile.read()
	print data
	global all_tokens
	all_tokens = []
	global indexed_tokens
	indexed_tokens = []
	try:
		tokenStream = tokenize.tokenize(StringIO.StringIO(data).readline, handle_token)
	except tokenize.TokenError:
   		pass
	one_hot_file = vocabularize_tokens(all_tokens, False)

	windowInd = 0
	while windowInd <= int((int(len(one_hot_file)) - 10)):
		toPass = []
		for x in range(10):
			y = x + windowInd
			print y
			print len(one_hot_file)
			toPass.append(one_hot_file[y])
		a = np.array(toPass).astype(int)
		assert len(a) == 10
		print a
		yield a
		windowInd += 1
	print "done radha"
	#print len(one_hot_file)



def predict(fileName):
	# load YAML and create model
	yaml_file = open('model_l.yaml', 'r')
	loaded_model_yaml = yaml_file.read()
	yaml_file.close()
	loaded_model = model_from_yaml(loaded_model_yaml)
	# load weights into new model
	loaded_model.load_weights("model_l.h5")
	print("Loaded model from disk")
 
	# evaluate loaded model on test data
	opt = optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.5)
	loaded_model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

	outPredict = loaded_model.predict_generator(getFileTokens(fileName), 225, 3, verbose=1)

	print outPredict
	print len(outPredict)	

	inds = []
	for x in range(len(list(outPredict))):
		inds.append(list(outPredict[x]).index(max(outPredict[x])))
	print max(outPredict[0])
	print list(outPredict[0]).index(max(outPredict[0]))
	print "MAX"
        countGood = -1
        countIns = -1
	countDel = -1
	iterInd = 0
	for b in inds:
		if iterInd == 3:
			iterInd = 0
		
		if iterInd == 0:
               		if b == 0:
				countGood += 1
		if iterInd == 1: 		
			if b == 3:
				countIns += 1
		if iterInd == 2:
			if b == 2:
				countDel += 1
		iterInd += 1
		#print b
        print len(inds)
	print countGood
	print countIns
	print countDel	

if __name__ == '__main__':
	fileName = sys.argv[1]
	predict(fileName)

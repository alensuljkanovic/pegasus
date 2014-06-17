__author__ = 'Alen Suljkanovic'


class Rule(object):

    def __init__(self, name, alternatives):
        self.name = name
        self.alternatives = alternatives


class Pegasus(object):

    def __init__(self, context_free_grammar, debug):
        self.context_free_grammar = context_free_grammar
        self.debug = debug

    def parse_cfg(self):
        lines = self.context_free_grammar.split(';')
        seq = ''
        rule_name = ''
        for i, line in enumerate(lines):
            line = line.strip()
            if line == '':
                continue

            options = line.split(':')
            if len(options) == 0:
                continue

            for j, option in enumerate(options):
                if j == 0:
                    rule_name = option.strip()
                else:
                    if option.find('|') != -1:
                        alternatives = option.split('|')
                        recursive = self.avoid_left_recursion(rule_name, alternatives)
                        seq = self.create_peg_sequence(rule_name, alternatives, recursive)
                        #print(seq)
                    elif option.find(' ') != -1:
                        alternatives = option.split(' ')
                        seq = self.create_ordered_choice(alternatives)

            rule = Rule(rule_name, seq)
            print(rule.name + ' : ' + rule.alternatives)

    def create_peg_sequence(self, rule_name, alternatives, recursive):
        sequence = '['
        count = len(alternatives)
        if recursive is not None:
            sequence = alternatives[0].strip() + ', ' + recursive
            return sequence

        for i, alt in enumerate(alternatives):
            #Trimming whitespaces
            alt = alt.strip()

            comment_index = alt.find('//')
            if comment_index != -1:
                alt = alt[0:comment_index]

            posible_substrings = alt.split(' ')
            if len(posible_substrings) > 1:
                alt = self.create_ordered_choice(posible_substrings)
            if alt.endswith('+'):
                alt = self.create_one_or_more(alt)
            elif alt.endswith('?'):
                alt = self.create_optional(alt)

            sequence += alt
            if i != count - 1:
                sequence += ','

        sequence += ']'
        return sequence

    def create_one_or_more(self, alt):
        return 'OneOrMore(' + alt.replace('+', '').lstrip() + ')'

    def create_optional(self, alt):
        return 'Optional(' + alt.replace('?', '').lstrip() + ')'

    def create_ordered_choice(self, order):
        ordered = '('
        count = len(order)
        if count == 2 and order[0] == '':
            return order[1]

        for i, order_member in enumerate(order):
            if len(order_member) == 0:
                continue

            if order_member.endswith('+'):
                order_member = self.create_one_or_more(order_member)
            elif order_member.endswith('?'):
                order_member = self.create_optional(order_member)

            ordered += order_member
            if i != count - 1:
                ordered += ','
        ordered += ')'
        return ordered

    def avoid_left_recursion(self, rule_name, alternatives):
        operators = []
        for i, alt in enumerate(alternatives):
            alt = alt.strip()
            index = alt.find(rule_name)
            if index == 0:
                alt = alt[len(rule_name): len(alt)].strip()
                index2 = alt.find(' ')
                operator = alt[0: index2]
                operators.append(operator)

        ret_val = 'ZeroOrMore(['

        length = len(operators)
        if length == 0:
            return None

        for i, op in enumerate(operators):
            ret_val += op
            if i != length - 1:
                ret_val += ','

        ret_val += '],  ' + alternatives[0].strip() + ')'
        return ret_val


if __name__ == "__main__":
    test_data = """

          unaryOperator
: '&' | '*' | '+' | '-' | '~' | '!'
;

castExpression
: unaryExpression
| '(' typeName ')' castExpression
| '__extension__' '(' typeName ')' castExpression
;

multiplicativeExpression
: castExpression
| multiplicativeExpression '*' castExpression
| multiplicativeExpression '/' castExpression
| multiplicativeExpression '%' castExpression
;

additiveExpression
: multiplicativeExpression
| additiveExpression '+' multiplicativeExpression
| additiveExpression '-' multiplicativeExpression
;

shiftExpression
: additiveExpression
| shiftExpression '<<' additiveExpression
| shiftExpression '>>' additiveExpression
;

relationalExpression
: shiftExpression
| relationalExpression '<' shiftExpression
| relationalExpression '>' shiftExpression
| relationalExpression '<=' shiftExpression
| relationalExpression '>=' shiftExpression
;

equalityExpression
: relationalExpression
| equalityExpression '==' relationalExpression
| equalityExpression '!=' relationalExpression
;

andExpression
: equalityExpression
| andExpression '&' equalityExpression
;

exclusiveOrExpression
: andExpression
| exclusiveOrExpression '^' andExpression
;

inclusiveOrExpression
: exclusiveOrExpression
| inclusiveOrExpression '|' exclusiveOrExpression
;

logicalAndExpression
: inclusiveOrExpression
| logicalAndExpression '&&' inclusiveOrExpression
;

logicalOrExpression
: logicalAndExpression
| logicalOrExpression '||' logicalAndExpression
;

conditionalExpression
: logicalOrExpression ('?' expression ':' conditionalExpression)?
;

assignmentExpression
: conditionalExpression
| unaryExpression assignmentOperator assignmentExpression
;

assignmentOperator
: '=' | '*=' | '/=' | '%=' | '+=' | '-=' | '<<=' | '>>=' | '&=' | '^=' | '|='
;

expression
: assignmentExpression
| expression ',' assignmentExpression
;

constantExpression
: conditionalExpression
;

declaration
: declarationSpecifiers initDeclaratorList? ';'
| staticAssertDeclaration
;

declarationSpecifiers
: declarationSpecifier+
;

declarationSpecifiers2
: declarationSpecifier+
;

declarationSpecifier
: storageClassSpecifier
| typeSpecifier
| typeQualifier
| functionSpecifier
| alignmentSpecifier
;

initDeclaratorList
: initDeclarator
| initDeclaratorList ',' initDeclarator
;

initDeclarator
: declarator
| declarator '=' initializer
;

storageClassSpecifier
: 'typedef'
| 'extern'
| 'static'
| '_Thread_local'
| 'auto'
| 'register'
;

typeSpecifier
: ('void'
| 'char'
| 'short'
| 'int'
| 'long'
| 'float'
| 'double'
| 'signed'
| 'unsigned'
| '_Bool'
| '_Complex'
| '__m128'
| '__m128d'
| '__m128i')
| '__extension__' '(' ('__m128' | '__m128d' | '__m128i') ')'
| atomicTypeSpecifier
| structOrUnionSpecifier
| enumSpecifier
| typedefName
| '__typeof__' '(' constantExpression ')' // GCC extension
;

structOrUnionSpecifier
: structOrUnion Identifier? '{' structDeclarationList '}'
| structOrUnion Identifier
;

structOrUnion
: 'struct'
| 'union'
;


        """
    pegasus = Pegasus(test_data, True)
    pegasus.parse_cfg()
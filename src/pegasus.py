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
                        seq = self.create_peg_sequence(alternatives)
                        #print(seq)
                    elif option.find(' ') != -1:
                        alternatives = option.split(' ')
                        seq = self.create_ordered_choice(alternatives)

            rule = Rule(rule_name, seq)
            print(rule.name + ' : ' + rule.alternatives)

    def create_peg_sequence(self, alternatives):
        sequence = '['
        count = len(alternatives)
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

if __name__ == "__main__":
    test_data = """

            enumSpecifier
            : 'enum' Identifier? '{' enumeratorList '}'
            | 'enum' Identifier? '{' enumeratorList ',' '}'
            | 'enum' Identifier
            ;

            enumeratorList
            : enumerator
            | enumeratorList ',' enumerator
            ;

            enumerator
            : enumerationConstant
            | enumerationConstant '=' constantExpression
            ;
        """
    pegasus = Pegasus(test_data, True)
    pegasus.parse_cfg()
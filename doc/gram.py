import re
from pathlib import Path

#Copy PDF grammar here!
grammar = """
transition ::= if guarded_arrow ;
| [[ scope ]] target ;
[S1-078] guarded_arrow ::= ( expr ) arrow
[S1-079] arrow ::= [[ scope ]] (( target | fork ))
[S1-080] target ::= (( restart | resume )) [[ luid | id ]]
[S1-081] fork ::= if guarded_arrow
{{ elsif guarded_arrow }}
[[ else arrow ]]
end
| {{ fork_priority }} end
[S1-082] fork_priority ::= priority if guarded_arrow
| priority else arrow
"""
pos = 0
output = Path(__file__).parent / 'gram.out'
with output.open('w') as fd:
    for line in grammar.splitlines(True):
        # suppress req tags
        line = re.sub('\[S1.\d+\]\s*', '', line)
        # emph words (work to do for keyword or atoms)
        line = re.sub('(\w+)', r'*\1*', line)
        # adapt '|' position
        m = re.search('::=', line)
        if m:
            pos = m.start()
        line = re.sub('^\s*\|', (' '*pos)+'|', line)

        fd.write(f"| {line}")
print(f"result: {output}")
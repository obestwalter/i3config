#!/usr/bin/env python
from pprint import pprint

import i3

pprint(i3.filter(nodes=[], focused=True, tree=i3.get_tree()))

#pprint(i3.get_tree())

exit()
outputs = i3.get_outputs()

# set current workspace to output 0
i3.workspace(outputs[0]['current_workspace'])

# ..and move it to the other output.
# outputs wrap, so the right of the right is left ;)
i3.move__workspace__to__output__right("workspace")

# rinse and repeat
i3.workspace(outputs[1]['current_workspace'])
i3.move__workspace__to__output__right()

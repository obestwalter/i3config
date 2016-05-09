#!/usr/bin/python2.7

import i3

outputs = i3.get_outputs()

# set current workspace to output 0
i3.workspace(outputs[0]['current_workspace'])

# ..and move it to the other output.
# outputs wrap, so the right of the right is left ;)
i3.move__workspace__to__output__right()

# rinse and repeat
i3.workspace(outputs[1]['current_workspace'])
i3.move__workspace__to__output__right()

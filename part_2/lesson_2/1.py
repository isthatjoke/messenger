a = {'integer': 1}

print(a)
a.pop('integer')
print(a)

import platform
import os, pprint
print(platform.system())
print(os.name)
b = os.environ
pprint.pprint(a)
c = [1, 2, 3, 4]

pprint.pprint(c)
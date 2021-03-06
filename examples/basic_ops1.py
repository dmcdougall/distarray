from __future__ import print_function
import distarray as ipda


a = ipda.random.rand((10,100,100), dist=('n','b','c'))
b = ipda.random.rand((10,100,100), dist=('n','b','c'))
c = 0.5*ipda.sin(a) + 0.5*ipda.cos(b)
print(c.sum(), c.mean(), c.std(), c.var())

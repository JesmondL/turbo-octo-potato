# Business logics
import abc

class Base(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, input):
        return 'Abstract'

    @abc.abstractmethod
    def save(self, output, data):
        return 'Abstract'

class Implementation(Base):

    def load(self, input):
        return 'Implementation'

    def save(self, output, data):
        return 'Implementation'

i = Implementation()
print 'Implementation', i.value
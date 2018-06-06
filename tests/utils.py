class ClassPropertyDescriptor(object):
    """Based on https://stackoverflow.com/questions/5189699/how-to-make-a-class-property"""

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, klass):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    return ClassPropertyDescriptor(classmethod(func))

class bar:
    
    def __init__(self, xxx):
        self.xxx = xxx
        map(self.foo, xxx)

    def foo(self, var, **args):
        print var, *args
    
    def partial(self, fx, *args):
        return fx(args)

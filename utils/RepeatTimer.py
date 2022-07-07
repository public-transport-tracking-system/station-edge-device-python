from threading import Timer

class RepeatTimer(Timer):  
    def run(self):  
        while not self.finished.wait(self.interval):  
            print(*self.args)
            self.function(*self.args,**self.kwargs)  
            print(' ')
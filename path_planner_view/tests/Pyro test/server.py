import Pyro4

@Pyro4.expose
class JokeGen(object):
    def __init__(self):
        self.jokevar = "Joke"

    def joke(self, name):
        return "Sorry "+name+", I don't know any jokes."

def main():
    Pyro4.Daemon.serveSimple(
            {
                JokeGen: "example.jokegen"
            },
            ns = True)

if __name__=="__main__":
    main()

from mod import movie
from mod import help
def dispacher(key):

    map={"mv":1,
    "help":2}
    key=key.split()
    if key[0]=='mv':
        movieHandle=movie.Movie()
        if len(key)==2:
            return movieHandle.getMovie(key[1])
        if len(key)==3:
            return movieHandle.getBtlink(key[1])

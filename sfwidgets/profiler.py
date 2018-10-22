import cProfile
import pstats

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def profile_it(func):
    def wrapped(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()  # start profiling
        res = func(*args, **kwargs)
        pr.disable()  # end profiling
        s = StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        return res

    return wrapped

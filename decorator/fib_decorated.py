#!/usr/bin/env

"""
Write a decorator that stores the result of a function call and returns the cached version in 
subsequent calls (with the same parameters) for 5 minutes, or ten times whichever comes first.
"""



import functools
import time
import sys
import os

printDetailTrace = False #just default, runtime assigment at the bottom


def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    def _d(fn):
        return functools.update_wrapper(d(fn), fn)
    return _d
#decorator = decorator(decorator)


def disabled(f):
    # Example: Use trace = disabled to turn off trace decorators
    return f


@decorator
def n_ary(f):
    """Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x."""
    def n_ary_f(x, *args):
        return x if not args else f(x, n_ary_f(*args))
    return n_ary_f


fib_msg = ['fib_msg']
memo_msg = ['memo_msg']


@decorator
def trace(f):
    print 'trace', f.__name__, f
    indent = '   '
    def _f(*args):
        signature = '%s(%s)' % (f.__name__, ', '.join(map(repr, args)))
        print '%s--> %s' % (trace.level*indent, signature)
        trace.level += 1
        try:
            result = f(*args)
            print '%s<-- %s == %s  %s   %s' \
                   % ((trace.level-1)*indent, signature, result, ''.join(fib_msg[0]), ''.join(memo_msg[0]))
            fib_msg[0], memo_msg[0] = ' ', ' '
        finally:
            trace.level -= 1
        return result
    trace.level = 0
    return _f


@decorator
@trace
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        signature = '%s(%s)' % (f.__name__, ', '.join(map(repr, args)))
        (last, now, elapsed)= elapsed_time(f, args)
        no_of_calls = callcounts_fun_args[args]
        if(printDetailTrace):
            callstamp = "last call: %.2f, this call: %.2f, elapsed: %.0f" % (last, now, elapsed)
        else:
            callstamp = ''         
        try:
            x = cache[args] #will raise error if there is no key in cache
            if validate_cache(f, args)[0]:
                result = cache[args]
                memo_msg[0] = 'memo: ' +  signature + 'hit(valid) '+ callstamp
                return result
            else:
                result = f(*args)
                cache[args] = result
                memo_msg[0] = 'memo: ' + signature + 'hit(invalid) ' + callstamp
                return result
        except KeyError:
            memo_msg[0] =  'memo: ' + signature + 'miss ' + callstamp
            result = f(*args)
            cache[args] = result
            return result
        except TypeError:
            # some element of args can't be a dict key
            memo_msg[0] = 'memo: ' + signature + 'error' + callstamp
            sys.exit(1)
    _f.cache = cache
    print 'memo : ', memo_msg[0]
    return _f


@trace
def validate_cache(f, args):
    validate_cache.signature = '%s(%s)' % (f.__name__, ', '.join(map(repr, args)))
    valid = [False]
    def _f(args):
        try:
            no_of_calls = callcounts_fun_args[args]
            if (no_of_calls > 1 and no_of_calls % cashe_inv_after_calls == 1) or cashe_inv_after_calls ==1:
                valid[0] = False
            elif lastcall_fun_args_timestamp[args][1] - lastcall_fun_args_timestamp[args][0] > cashe_inv_after_sec:
                valid[0] = False
            else:
                valid[0] = True
        except:
            print 'validate_cache? exception', validate_cache.signature, ' valid: ', valid
            sys.exit(1)
        return valid
    _f(args)
    return valid

@trace
def elapsed_time(f, args):
    time = [0,0,0]
    def _f(args):
        time[0] = last_time = lastcall_fun_args_timestamp[args][0]
        time[1] = this_time = lastcall_fun_args_timestamp[args][1]
        time[2] = elapsed = (this_time - last_time) / 60.0
        return time
    _f(args)
    return time


@decorator
@trace
def countcalls(f):
    "Decorator that makes the function count calls to it, in callcounts[f]."
    def _f(*args):
        countcalls.signature = '%s(%s)' % (f.__name__, ', '.join(map(repr, args)))
        try: #count function calls
            callcounts_function[_f] += 1
        except KeyError:
            callcounts_function[_f] = 1
        except:
            print 'countcalls? exception', countcalls.signature
            sys.exit(1)

        try: #count function calls with same arguments
            callcounts_fun_args[args] += 1
        except KeyError:
            callcounts_fun_args[args] = 1
        except:
            print 'countcalls? exception', countcalls.signature
            sys.exit(1)

        try: #remember last call and this call time
            last_time = lastcall_fun_args_timestamp[args][1]
            lastcall_fun_args_timestamp[args] = (last_time, time.time())
        except KeyError:
            lastcall_fun_args_timestamp[args] = (0, time.time())
        except:
            print 'countcalls? exception', countcalls.signature
            sys.exit(1)
        return f(*args)
    return _f
callcounts_function = {}
callcounts_fun_args = {}
lastcall_fun_args_timestamp = {}






@trace
@countcalls
@memo
def fib(n):
    if n == 0 or n == 1:
        fib_msg[0] = 'default fib(0|1) = 1'
        return 1
    else:
        fib_n = fib(n-1) + fib(n-2)
        fib_msg[0] = 'calculation inside fib: fib(%i) + fib(%i) = fib(%i) = %i' % (n-1, n-2, n, fib_n)
        return fib_n




#invalidate cache after
cashe_inv_after_sec = 0.5
cashe_inv_after_calls = 3
run_for_sec = 2.0
fib_num = 3
printDetailTrace = False

def execute_fib_in_loop(change_fib_num):
    st = time.time()
    i=0
    while True:
       i=i+1
       print '\n\n\nrun: %i' % i
       if change_fib_num:
           fib(fib_num + i)
       else:
           fib(fib_num)
       et = time.time()
       print et - st
       if et - st > run_for_sec:
           break



#path = os.path.join(os.getcwd(), 'Documents', 'decorator.txt')
path = os.path.join(os.getcwd(), 'decorator.txt')
sys.stdout = open(path, "w+")


execute_fib_in_loop(False)


# This is the meat of the Online Python Tutor back-end.  It implements a
# full logger for Python program execution (based on pdb, the standard
# Python debugger imported via the bdb module), printing out the values
# of all in-scope data structures after each executed instruction.

import sys
import bdb
import re
import traceback
import types

is_python3 = (sys.version_info[0] == 3)

import io as StringIO
import io 
import encoder

MAX_EXECUTED_LINES = 1000 

DEBUG = True

BREAKPOINT_STR = '#break'

CLASS_RE = re.compile('class\s+')

# simple sandboxing scheme:
#
# - use resource.setrlimit to deprive this process of ANY file descriptors
#   (which will cause file read/write and subprocess shell launches to fail)
# - restrict user builtins and module imports
#   (beware that this is NOT foolproof at all ... there are known flaws!)
#
# ALWAYS use defense-in-depth and don't just rely on these simple mechanisms
try:
  import resource
  resource_module_loaded = True
except ImportError:
  resource_module_loaded = False

__html__ = None
def setHTML(htmlStr):
  global __html__
  __html__ = htmlStr

__css__ = None
def setCSS(cssStr):
  global __css__
  __css__ = cssStr

__js__ = None
def setJS(jsStr):
  global __js__
  __js__ = jsStr

BUILTIN_IMPORT = __builtins__['__import__']

ALLOWED_STDLIB_MODULE_IMPORTS = ('math', 'random', 'time', 'datetime',
                          'functools', 'itertools', 'operator', 'string',
                          'collections', 're', 'json',
                          'heapq', 'bisect', 'copy', 'hashlib')

# allow users to import but don't explicitly import it since it's
# already been done above
OTHER_STDLIB_WHITELIST = ('StringIO', 'io')

for m in ALLOWED_STDLIB_MODULE_IMPORTS:
  __import__(m)

# Restrict imports to a whitelist
def __restricted_import__(*args):
  # filter args to ONLY take in real strings so that someone can't
  # subclass str and bypass the 'in' test on the next line
  args = [e for e in args if type(e) is str]

  if args[0] in ALLOWED_STDLIB_MODULE_IMPORTS + OTHER_STDLIB_WHITELIST:
    imported_mod = BUILTIN_IMPORT(*args)
    
    # somewhat weak protection against imported modules that contain one
    # of these troublesome builtins. again, NOTHING is foolproof ...
    # just more defense in depth :)
    for mod in ('os', 'sys', 'posix', 'gc'):
      if hasattr(imported_mod, mod):
        delattr(imported_mod, mod)

    return imported_mod
  else:
    raise ImportError('{0} not supported'.format(args[0]))

# Support interactive user input by:
#
# 1. running the entire program up to a call to raw_input (or input in py3),
# 2. bailing and returning a trace ending in a special 'raw_input' event,
# 3. letting the web frontend issue a prompt to the user to grab a string,
# 4. RE-RUNNING the whole program with that string added to input_string_queue,
# 5. which should bring execution to the next raw_input call (if
#    available), or to termination.
# Repeat until no more raw_input calls are encountered.
# Note that this is mad inefficient, but is simple to implement!

import random
random.seed(0)

input_string_queue = []

class RawInputException(Exception):
  pass

def raw_input_wrapper(prompt=''):
  if input_string_queue:
    input_str = input_string_queue.pop(0)

    # write the prompt and user input to stdout, to emulate what happens
    # at the terminal
    sys.stdout.write(str(prompt)) # always convert prompt into a string
    sys.stdout.write(input_str + "\n") # newline to simulate the user hitting Enter
    return input_str
  raise RawInputException(str(prompt)) # always convert prompt into a string

IGNORE_VARS = set(('__user_stdout__', '__OPT_toplevel__', '__builtins__', '__name__', '__exception__', '__doc__', '__package__'))

def get_user_stdout(frame):
  my_user_stdout = frame.f_globals['__user_stdout__']
  return my_user_stdout.getvalue()

# at_global_scope should be true only if 'frame' represents the global scope
def get_user_globals(frame, at_global_scope=False):
  d = filter_var_dict(frame.f_globals)

  # print out list objects being built up in Python 2.x list comprehensions
  # (which don't have its own special <listcomp> frame, sadly)
  if not is_python3 and hasattr(frame, 'f_valuestack'):
    for (i, e) in enumerate([e for e in frame.f_valuestack if type(e) is list]):
      d['_tmp' + str(i+1)] = e

  # also filter out __return__ for globals only, but NOT for locals
  if '__return__' in d:
    del d['__return__']
  return d

def get_user_locals(frame):
  ret = filter_var_dict(frame.f_locals)

  # special printing of list/set/dict comprehension objects as they are
  # being built up incrementally ...
  f_name = frame.f_code.co_name
  if hasattr(frame, 'f_valuestack'):
    # for dict and set comprehensions, which have their own frames:
    if f_name.endswith('comp>'):
      for (i, e) in enumerate([e for e in frame.f_valuestack
                               if type(e) in (list, set, dict)]):
        ret['_tmp' + str(i+1)] = e

  return ret

def filter_var_dict(d):
  ret = {}
  for (k,v) in d.items():
    if k not in IGNORE_VARS:
      ret[k] = v
  return ret

# yield all function objects locally-reachable from frame,
# making sure to traverse inside all compound objects ...
def visit_all_locally_reachable_function_objs(frame):
  for (k, v) in get_user_locals(frame).items():
    for e in visit_function_obj(v, set()):
      if e: # only non-null if it's a function object
        assert type(e) in (types.FunctionType, types.MethodType)
        yield e

def visit_function_obj(v, ids_seen_set):
  v_id = id(v)

  # to prevent infinite loop
  if v_id in ids_seen_set:
    yield None
  else:
    ids_seen_set.add(v_id)

    typ = type(v)
    
    # simple base case
    if typ in (types.FunctionType, types.MethodType):
      yield v

    # recursive cases
    elif typ in (list, tuple, set):
      for child in v:
        for child_res in visit_function_obj(child, ids_seen_set):
          yield child_res

    elif typ == dict or encoder.is_class(v) or encoder.is_instance(v):
      contents_dict = None

      if typ == dict:
        contents_dict = v
      # warning: some classes or instances don't have __dict__ attributes
      elif hasattr(v, '__dict__'):
        contents_dict = v.__dict__

      if contents_dict:
        for (key_child, val_child) in contents_dict.items():
          for key_child_res in visit_function_obj(key_child, ids_seen_set):
            yield key_child_res
          for val_child_res in visit_function_obj(val_child, ids_seen_set):
            yield val_child_res

    # degenerate base case
    yield None

class PGLogger(bdb.Bdb):

    def __init__(self, finalizer_func):
        bdb.Bdb.__init__(self)
        self._wait_for_mainpyfile = 0

        # a function that takes the output trace as a parameter and
        # processes it
        self.finalizer_func = finalizer_func

        # each entry contains a dict with the information for a single
        # executed line
        self.trace = []

        # if this is true, don't put any more stuff into self.trace
        self.done = False

        # if this is non-null, don't do any more tracing until a
        # 'return' instruction with a stack gotten from
        # get_stack_code_IDs() that matches wait_for_return_stack
        self.wait_for_return_stack = None

        #http://stackoverflow.com/questions/2112396/in-python-in-google-app-engine-how-do-you-capture-output-produced-by-the-print
        self.GAE_STDOUT = sys.stdout

        # Key:   function object
        # Value: parent frame
        self.closures = {}

        # Key:   code object for a lambda
        # Value: parent frame
        self.lambda_closures = {}

        # set of function objects that were defined in the global scope
        self.globally_defined_funcs = set()

        # Key: frame object
        # Value: monotonically increasing small ID, based on call order
        self.frame_ordered_ids = {}
        self.cur_frame_id = 1

        # List of frames to KEEP AROUND after the function exits.
        # If cumulative_mode is True, then keep ALL frames in
        # zombie_frames; otherwise keep only frames where
        # nested functions were defined within them.
        self.zombie_frames = []

        # set of elements within zombie_frames that are also
        # LEXICAL PARENTS of other frames
        self.parent_frames_set = set()

        # all globals that ever appeared in the program, in the order in
        # which they appeared. note that this might be a superset of all
        # the globals that exist at any particular execution point,
        # since globals might have been deleted (using, say, 'del')
        self.all_globals_in_order = []

        # very important for this single object to persist throughout
        # execution, or else canonical small IDs won't be consistent.
        self.encoder = encoder.ObjectEncoder()

        self.executed_script = None # Python script to be executed!

        self.prev_lineno = -1 # keep track of previous line just executed


    def get_frame_id(self, cur_frame):
      return self.frame_ordered_ids[cur_frame]

    # Returns the (lexical) parent of a function value.
    def get_parent_of_function(self, val):
      if val in self.closures:
          return self.get_frame_id(self.closures[val])
      elif val in self.lambda_closures:
          return self.get_frame_id(self.lambda_closures[val])
      else:
        return None

    # Returns the (lexical) parent frame of the function that was called
    # to create the stack frame 'frame'.
    def get_parent_frame(self, frame):
      for (func_obj, parent_frame) in self.closures.items():
        # ok, there's a possible match, but let's compare the
        # local variables in parent_frame to those of frame
        # to make sure. this is a hack that happens to work because in
        # Python, each stack frame inherits ('inlines') a copy of the
        # variables from its (lexical) parent frame.
        if func_obj.__code__ == frame.f_code:
          all_matched = True
          for k in frame.f_locals:
            # Do not try to match local names
            if k in frame.f_code.co_varnames:
              continue
            if k != '__return__' and k in parent_frame.f_locals:
              if parent_frame.f_locals[k] != frame.f_locals[k]:
                all_matched = False
                break

          if all_matched:
            return parent_frame

      for (lambda_code_obj, parent_frame) in self.lambda_closures.items():
        if lambda_code_obj == frame.f_code:
          return parent_frame

      return None

    def lookup_zombie_frame_by_id(self, frame_id):
      for e in self.zombie_frames:
        if self.get_frame_id(e) == frame_id:
          return e
      assert False 

    def forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None

    def setup(self, f, t):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, t)
        self.curframe = self.stack[self.curindex][0]

    # should be a reasonably unique ID to match calls and returns:
    def get_stack_code_IDs(self):
        return [id(e[0].f_code) for e in self.stack]


    # Override Bdb methods

    def user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function."""
        # TODO: figure out a way to move this down to 'def interaction'
        # or right before self.trace.append ...
        if self.done: return

        if self._wait_for_mainpyfile:
            return
        if self.stop_here(frame):
            # delete __return__ so that on subsequent calls to
            # a generator function, the OLD yielded (returned)
            # value gets deleted from the frame ...
            try:
              del frame.f_locals['__return__']
            except KeyError:
              pass

            self.interaction(frame, None, 'call')

    def user_line(self, frame):
        """This function is called when we stop or break at this line."""
        if self.done: return

        if self._wait_for_mainpyfile:
            if (self.canonic(frame.f_code.co_filename) != "<string>" or
                frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = 0
        self.interaction(frame, None, 'step_line')

    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        if self.done: return

        frame.f_locals['__return__'] = return_value
        self.interaction(frame, None, 'return')

    def user_exception(self, frame, exc_info):
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""
        if self.done: return

        exc_type, exc_value, exc_traceback = exc_info
        frame.f_locals['__exception__'] = exc_type, exc_value
        if type(exc_type) == type(''):
            exc_type_name = exc_type
        else: exc_type_name = exc_type.__name__

        if exc_type_name == 'RawInputException':
          raw_input_arg = str(exc_value.args[0]) # make sure it's a string so it's JSON serializable!
          self.trace.append(dict(event='raw_input', prompt=raw_input_arg))
          self.done = True
        else:
          self.interaction(frame, exc_traceback, 'exception')

    def get_script_line(self, n):
        return self.executed_script_lines[n-1]

    # General interaction function

    def interaction(self, frame, traceback, event_type):
        self.setup(frame, traceback)
        tos = self.stack[self.curindex]
        top_frame = tos[0]
        lineno = tos[1]

        # don't trace inside of ANY functions that aren't user-written code
        # (e.g., those from imported modules -- e.g., random, re -- or the
        # __restricted_import__ function in this file)
        #
        # empirically, it seems like the FIRST entry in self.stack is
        # the 'run' function from bdb.py, but everything else on the
        # stack is the user program's "real stack"

        # Look only at the "topmost" frame on the stack ...

        # it seems like user-written code has a filename of '<string>',
        # but maybe there are false positives too?
        if self.canonic(top_frame.f_code.co_filename) != '<string>':
          return
        # also don't trace inside of the magic "constructor" code
        if top_frame.f_code.co_name == '__new__':
          return
        # or __repr__, which is often called when running print statements
        if top_frame.f_code.co_name == '__repr__':
          return

        # if top_frame.f_globals doesn't contain the sentinel '__OPT_toplevel__',
        # then we're in another global scope altogether, so skip it!
        # (this comes up in tests/backend-tests/namedtuple.txt)
        if '__OPT_toplevel__' not in top_frame.f_globals:
          return

        # don't trace if wait_for_return_stack is non-null ...
        if self.wait_for_return_stack:
          if event_type == 'return' and \
             (self.wait_for_return_stack == self.get_stack_code_IDs()):
            self.wait_for_return_stack = None # reset!
          return # always bail!
        else:
          # Skip all "calls" that are actually class definitions, since
          # those faux calls produce lots of ugly cruft in the trace.
          #
          # NB: Only trigger on calls to functions defined in
          # user-written code (i.e., co_filename == '<string>'), but that
          # should already be ensured by the above check for whether we're
          # in user-written code.
          if event_type == 'call':
            func_line = self.get_script_line(top_frame.f_code.co_firstlineno)
            if CLASS_RE.match(func_line.lstrip()): # ignore leading spaces
              self.wait_for_return_stack = self.get_stack_code_IDs()
              return

        self.encoder.reset_heap() # VERY VERY VERY IMPORTANT,
                                  # or else we won't properly capture heap object mutations in the trace!

        if event_type == 'call':
          # Don't be so strict about this assertion because it FAILS
          # when you're calling a generator (not for the first time),
          # since that frame has already previously been on the stack ...
          #assert top_frame not in self.frame_ordered_ids

          self.frame_ordered_ids[top_frame] = self.cur_frame_id
          self.cur_frame_id += 1

        # only render zombie frames that are NO LONGER on the stack
        #
        # subtle: self.stack[:self.curindex+1] is the real stack, since
        # everything after self.curindex+1 is beyond the top of the
        # stack. this seems to be relevant only when there's an exception,
        # since the ENTIRE stack is preserved but self.curindex
        # starts decrementing as the exception bubbles up the stack.
        cur_stack_frames = [e[0] for e in self.stack[:self.curindex+1]]
        zombie_frames_to_render = [e for e in self.zombie_frames if e not in cur_stack_frames]


        # each element is a pair of (function name, ENCODED locals dict)
        encoded_stack_locals = []

        # returns a dict with keys: function name, frame id, id of parent frame, encoded_locals dict
        def create_encoded_stack_entry(cur_frame):
          ret = {}

          parent_frame_id_list = []

          f = cur_frame
          while True:
            p = self.get_parent_frame(f)
            if p:
              pid = self.get_frame_id(p)
              assert pid
              parent_frame_id_list.append(pid)
              f = p
            else:
              break

          cur_name = cur_frame.f_code.co_name

          if cur_name == '':
            cur_name = 'unnamed function'

          # augment lambdas with line number
          if cur_name == '<lambda>':
            cur_name += encoder.create_lambda_line_number(cur_frame.f_code,
                                                             self.encoder.line_to_lambda_code)

          # encode in a JSON-friendly format now, in order to prevent ill
          # effects of aliasing later down the line ...
          encoded_locals = {}

          for (k, v) in get_user_locals(cur_frame).items():
            is_in_parent_frame = False

            # don't display locals that appear in your parents' stack frames,
            # since that's redundant
            for pid in parent_frame_id_list:
              parent_frame = self.lookup_zombie_frame_by_id(pid)
              if k in parent_frame.f_locals:
                # ignore __return__, which is never copied
                if k != '__return__':
                  # these values SHOULD BE ALIASES
                  # (don't do an 'is' check since it might not fire for primitives)
                  if parent_frame.f_locals[k] == v:
                      is_in_parent_frame = True

            if is_in_parent_frame and k not in cur_frame.f_code.co_varnames:
              continue

            # don't display some built-in locals ...
            if k == '__module__':
              continue

            encoded_val = self.encoder.encode(v, self.get_parent_of_function)
            encoded_locals[k] = encoded_val


          # order the variable names in a sensible way:

          # Let's start with co_varnames, since it (often) contains all
          # variables in this frame, some of which might not exist yet.
          ordered_varnames = []
          for e in cur_frame.f_code.co_varnames:
            if e in encoded_locals:
              ordered_varnames.append(e)

          # sometimes co_varnames doesn't contain all of the true local
          # variables: e.g., when executing a 'class' definition.  in that
          # case, iterate over encoded_locals and push them onto the end
          # of ordered_varnames in alphabetical order
          for e in sorted(encoded_locals.keys()):
            if e != '__return__' and e not in ordered_varnames:
              ordered_varnames.append(e)

          # finally, put __return__ at the very end
          if '__return__' in encoded_locals:
            ordered_varnames.append('__return__')

          # doctor Python 3 initializer to look like a normal function (denero)
          if '__locals__' in encoded_locals:
            ordered_varnames.remove('__locals__')
            local = encoded_locals.pop('__locals__')
            if encoded_locals.get('__return__', True) is None:
              encoded_locals['__return__'] = local

          # crucial sanity checks!
          assert len(ordered_varnames) == len(encoded_locals)
          for e in ordered_varnames:
            assert e in encoded_locals

          return dict(func_name=cur_name,
                      is_parent=(cur_frame in self.parent_frames_set),
                      frame_id=self.get_frame_id(cur_frame),
                      parent_frame_id_list=parent_frame_id_list,
                      encoded_locals=encoded_locals,
                      ordered_varnames=ordered_varnames)

        i = self.curindex

        # look for whether a nested function has been defined during
        # this particular call:
        if i > 1: # i == 1 implies that there's only a global scope visible
          for v in visit_all_locally_reachable_function_objs(top_frame):
            if (v not in self.closures and \
                v not in self.globally_defined_funcs):

              # Look for the presence of the code object (v.func_code
              # for Python 2 or v.__code__ for Python 3) in the
              # constant pool (f_code.co_consts) of an enclosing
              # stack frame, and set that frame as your parent.
              #
              # This technique properly handles lambdas passed as
              # function parameters. e.g., this example:
              #
              # def foo(x):
              #   bar(lambda y: x + y)
              # def bar(a):
              #   print a(20)
              # foo(10)
              chosen_parent_frame = None
              # SUPER hacky but seems to work -- use reversed(self.stack)
              # because we want to traverse starting from the TOP of the stack
              # (most recent frame) and find the first frame containing
              # a constant code object that matches v.__code__ or v.func_code
              #
              # required for this example from Berkeley CS61a:
              #
              # def f(p, k):
              #     def g():
              #         print(k)
              #     if k == 0:
              #         f(g, 1)
              # f(None, 0)
              #
              # there are two calls to f, each of which defines a
              # closure g that should point to the respective frame.
              #
              # note that for the second call to f, the parent of the
              # g defined in there should be that frame, which is at
              # the TOP of the stack. this reversed() hack does the
              # right thing. note that if you don't traverse the stack
              # backwards, then you will mistakenly get the parent as
              # the FIRST f frame (bottom of the stack).
              for (my_frame, my_lineno) in reversed(self.stack):
                if chosen_parent_frame:
                  break

                for frame_const in my_frame.f_code.co_consts:
                  if frame_const is (v.__code__ if is_python3 else v.func_code):
                    chosen_parent_frame = my_frame
                    break

              # this condition should be False for functions declared in global scope ...
              if chosen_parent_frame in self.frame_ordered_ids:
                self.closures[v] = chosen_parent_frame
                self.parent_frames_set.add(chosen_parent_frame) # unequivocally add to this set!!!
                if not chosen_parent_frame in self.zombie_frames:
                  self.zombie_frames.append(chosen_parent_frame)
          else:
            # look for code objects of lambdas defined within this
            # function, which comes up in cases like line 2 of:
            # def x(y):
            #   (lambda z: lambda w: z+y)(y)
            #
            # x(42)
            if top_frame.f_code.co_consts:
              for e in top_frame.f_code.co_consts:
                if type(e) == types.CodeType and e.co_name == '<lambda>':
                  # TODO: what if it's already in lambda_closures?
                  self.lambda_closures[e] = top_frame
                  self.parent_frames_set.add(top_frame) # copy-paste from above
                  if not top_frame in self.zombie_frames:
                    self.zombie_frames.append(top_frame)
        else:
          # if there is only a global scope visible ...
          for (k, v) in get_user_globals(top_frame).items():
            if (type(v) in (types.FunctionType, types.MethodType) and \
                v not in self.closures):
              self.globally_defined_funcs.add(v)


        # climb up until you find '<module>', which is (hopefully) the global scope
        while True:
          cur_frame = self.stack[i][0]
          cur_name = cur_frame.f_code.co_name
          if cur_name == '<module>':
            break

          # do this check because in some cases, certain frames on the
          # stack might NOT be tracked, so don't push a stack entry for
          # those frames. this happens when you have a callback function
          # in an imported module. e.g., your code:
          #     def foo():
          #         bar(baz)
          #
          #     def baz(): pass
          #
          # imported module code:
          #     def bar(callback_func):
          #         callback_func()
          #
          # when baz is executing, the real stack is [foo, bar, baz] but
          # bar is in imported module code, so pg_logger doesn't trace
          # it, and it doesn't show up in frame_ordered_ids. thus, the
          # stack to render should only be [foo, baz].
          if cur_frame in self.frame_ordered_ids:
            encoded_stack_locals.append(create_encoded_stack_entry(cur_frame))
          i -= 1

        zombie_encoded_stack_locals = [create_encoded_stack_entry(e) for e in zombie_frames_to_render]


        # encode in a JSON-friendly format now, in order to prevent ill
        # effects of aliasing later down the line ...
        encoded_globals = {}
        for (k, v) in get_user_globals(tos[0], at_global_scope=(self.curindex <= 1)).items():
          encoded_val = self.encoder.encode(v, self.get_parent_of_function)
          encoded_globals[k] = encoded_val

          if k not in self.all_globals_in_order:
            self.all_globals_in_order.append(k)

        # filter out globals that don't exist at this execution point
        # (because they've been, say, deleted with 'del')
        ordered_globals = [e for e in self.all_globals_in_order if e in encoded_globals]
        assert len(ordered_globals) == len(encoded_globals)


        # merge zombie_encoded_stack_locals and encoded_stack_locals
        # into one master ordered list using some simple rules for
        # making it look aesthetically pretty
        stack_to_render = [];

        # first push all regular stack entries
        if encoded_stack_locals:
          for e in encoded_stack_locals:
            e['is_zombie'] = False
            e['is_highlighted'] = False
            stack_to_render.append(e)

          # highlight the top-most active stack entry
          stack_to_render[0]['is_highlighted'] = True


        # now push all zombie stack entries
        for e in zombie_encoded_stack_locals:

          e['is_zombie'] = True
          e['is_highlighted'] = False # never highlight zombie entries

          stack_to_render.append(e)

        # now sort by frame_id since that sorts frames in "chronological
        # order" based on the order they were invoked
        stack_to_render.sort(key=lambda e: e['frame_id'])

        # create a unique hash for this stack entry, so that the
        # frontend can uniquely identify it when doing incremental
        # rendering. the strategy is to use a frankenstein-like mix of the
        # relevant fields to properly disambiguate closures and recursive
        # calls to the same function
        for e in stack_to_render:
          hash_str = e['func_name']
          # frame_id is UNIQUE, so it can disambiguate recursive calls
          hash_str += '_f' + str(e['frame_id'])

          # needed to refresh GUI display ...
          if e['is_parent']:
            hash_str += '_p'

          # TODO: this is no longer needed, right? (since frame_id is unique)
          #if e['parent_frame_id_list']:
          #  hash_str += '_p' + '_'.join([str(i) for i in e['parent_frame_id_list']])
          if e['is_zombie']:
            hash_str += '_z'

          e['unique_hash'] = hash_str


        trace_entry = dict(line=lineno,event=event_type,func_name=tos[0].f_code.co_name,globals=encoded_globals,ordered_globals=ordered_globals,stack_to_render=stack_to_render,heap=self.encoder.get_heap(),stdout=get_user_stdout(tos[0]))

        global __html__, __css__, __js__
        if __html__:
          trace_entry['html_output'] = __html__
        if __css__:
          trace_entry['css_output'] = __css__
        if __js__:
          trace_entry['js_output'] = __js__

        # if there's an exception, then record its info:
        if event_type == 'exception':
          # always check in f_locals
          exc = frame.f_locals['__exception__']
          trace_entry['exception_msg'] = exc[0].__name__ + ': ' + str(exc[1])

        append_to_trace = True

        self.prev_lineno = lineno

        if append_to_trace:
          self.trace.append(trace_entry)


        if len(self.trace) >= MAX_EXECUTED_LINES:
          self.trace.append(dict(event='instruction_limit_reached', exception_msg='程序停止于' + str(MAX_EXECUTED_LINES) + '步. 请缩减你的代码,\n因为此工具不支持运行指令特别长的程序.'))
          self.force_terminate()

        self.forget()


    def _runscript(self, script_str, custom_globals=None):

        self.executed_script = script_str
        self.executed_script_lines = self.executed_script.splitlines()

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = 1


        # ok, let's try to sorta 'sandbox' the user script by not
        # allowing certain potentially dangerous operations.
        user_builtins = {}

        # ugh, I can't figure out why in Python 2, __builtins__ seems to
        # be a dict, but in Python 3, __builtins__ seems to be a module,
        # so just handle both cases ... UGLY!
        if type(__builtins__) is dict:
          builtin_items = __builtins__.items()
        else:
          assert type(__builtins__) is types.ModuleType
          builtin_items = []
          for k in dir(__builtins__):
            builtin_items.append((k, getattr(__builtins__, k)))

        for (k, v) in builtin_items:	
          if k == '__import__':
            user_builtins[k] = __restricted_import__
          else:
            if k == 'raw_input':
              user_builtins[k] = raw_input_wrapper
            elif k == 'input':
              if is_python3:
                # Python 3 input() is Python 2 raw_input()
                user_builtins[k] = raw_input_wrapper
            else:
              user_builtins[k] = v

        # TODO: we can disable these imports here, but a crafty user can
        # always get a hold of them by importing one of the external
        # modules, so there's no point in trying security by obscurity
        user_builtins['setHTML'] = setHTML
        user_builtins['setCSS'] = setCSS
        user_builtins['setJS'] = setJS

        user_stdout = StringIO.StringIO()

        sys.stdout = user_stdout
   
        self.ORIGINAL_STDERR = sys.stderr

        user_globals = {"__name__"    : "__main__",
                        "__builtins__" : user_builtins,
                        "__user_stdout__" : user_stdout,
                        # sentinel value for frames deriving from a top-level module
                        "__OPT_toplevel__": True}

        if custom_globals:
        	user_globals.update(custom_globals)

        try:
          # enforce resource limits RIGHT BEFORE running script_str

          # set ~200MB virtual memory limit AND a 5-second CPU time
          # limit (tuned for Webfaction shared hosting) to protect against
          # memory bombs such as:
          #   x = 2
          #   while True: x = x*x
          if resource_module_loaded:
            resource.setrlimit(resource.RLIMIT_AS, (200000000, 200000000))
            resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

            # protect against unauthorized filesystem accesses ...
            resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0)) # no opened files allowed

            # The posix module is a built-in and has a ton of OS access
            # facilities ... if you delete those functions from
            # sys.modules['posix'], it seems like they're gone EVEN IF
            # someone else imports posix in a roundabout way. Of course,
            # I don't know how foolproof this scheme is, though.
            # (It's not sufficient to just "del sys.modules['posix']";
            #  it can just be reimported without accessing an external
            #  file and tripping RLIMIT_NOFILE, since the posix module
            #  is baked into the python executable, ergh. Actually DON'T
            #  "del sys.modules['posix']", since re-importing it will
            #  refresh all of the attributes. ergh^2)
            for a in dir(sys.modules['posix']):
              delattr(sys.modules['posix'], a)
            # do the same with os
            for a in dir(sys.modules['os']):
              # 'path' is needed for __restricted_import__ to work
              # and 'stat' is needed for some errors to be reported properly
              if a not in ('path', 'stat'):
                delattr(sys.modules['os'], a)
            # ppl can dig up trashed objects with gc.get_objects()
            import gc
            for a in dir(sys.modules['gc']):
              delattr(sys.modules['gc'], a)
            del sys.modules['gc']

            # sys.modules contains an in-memory cache of already-loaded
            # modules, so if you delete modules from here, they will
            # need to be re-loaded from the filesystem.
            #
            # Thus, as an extra precaution, remove these modules so that
            # they can't be re-imported without opening a new file,
            # which is disallowed by resource.RLIMIT_NOFILE
            #
            # Of course, this isn't a foolproof solution by any means,
            # and it might lead to UNEXPECTED FAILURES later in execution.
            del sys.modules['os']
            del sys.modules['os.path']
            del sys.modules['sys']

          self.run(script_str, user_globals, user_globals)
        # sys.exit ...
        except SystemExit:
          #sys.exit(0)
          raise bdb.BdbQuit
        except:
          if DEBUG:
            traceback.print_exc()

          trace_entry = dict(event='uncaught_exception')

          (exc_type, exc_val, exc_tb) = sys.exc_info()
          if hasattr(exc_val, 'lineno'):
            trace_entry['line'] = exc_val.lineno
          if hasattr(exc_val, 'offset'):
            trace_entry['offset'] = exc_val.offset

          trace_entry['exception_msg'] = type(exc_val).__name__ + ": " +  str(exc_val)

          # SUPER SUBTLE! if ANY exception has already been recorded by
          # the program, then DON'T record it again as an uncaught_exception.
          # This looks kinda weird since the exact exception message doesn't
          # need to match up, but in practice, there should be at most only
          # ONE exception per trace.
          already_caught = False
          for e in self.trace:
            if e['event'] == 'exception':
              already_caught = True
              break

          if not already_caught:
            if not self.done:
              self.trace.append(trace_entry)

          raise bdb.BdbQuit # need to forceably STOP execution


    def force_terminate(self):
      #self.finalize()
      raise bdb.BdbQuit # need to forceably STOP execution

    def finalize(self):
      sys.stdout = self.GAE_STDOUT # very important!
      sys.stderr = self.ORIGINAL_STDERR

      assert len(self.trace) <= (MAX_EXECUTED_LINES + 1)

      res = self.trace

      # if the SECOND to last entry is an 'exception'
      # and the last entry is return from <module>, then axe the last
      # entry, for aesthetic reasons :)
      if len(res) >= 2 and \
         res[-2]['event'] == 'exception' and \
         res[-1]['event'] == 'return' and res[-1]['func_name'] == '<module>':
        res.pop()

      self.trace = res

      return self.finalizer_func(self.executed_script, self.trace)


import json

#后台脚本执行函数
def exec_script_str(script_str, raw_input_lst_json, finalizer_func):

  logger = PGLogger(finalizer_func)
  # TODO: refactor these NOT to be globals
  global input_string_queue
  input_string_queue = []
  if raw_input_lst_json:
    # TODO: if we want to support unicode, remove str() cast
    input_string_queue = [str(e) for e in json.loads(raw_input_lst_json)]

  #print(input_string_queue, sys.stderr)
  global __html__, __css__, __js__
  __html__, __css__, __js__ = None, None, None

  try:
    logger._runscript(script_str)
  except bdb.BdbQuit:
    pass
  finally:
    logger.finalize()

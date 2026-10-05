# Python
@short: Python
@subtitle: The thirty questions that come up in every screen
@tier: foundation
@prereq: none
@blurb: These appear in the phone screen and again in the technical round. The answers are short on purpose --- one or two sentences each. Say the sentence, stop, and let them ask the follow-up.
@objectives:
- Explain Python's core data types and when each is the right one
- Describe generators, decorators and context managers in plain words
- Answer the GIL question without reciting a paragraph
- Link an answer back to your own code wherever you can

## Data types

#### Q3.1 — List vs tuple?
A list can be changed after you make it; a tuple can't. Because a tuple never
changes, Python can use it as a dictionary key — a list can't be used that
way.

#### Q3.2 — What is a dictionary, and how fast is a lookup?
It's a lookup table: you give it a name, it gives you back the thing. Looking
something up takes the same tiny amount of time whether the dictionary holds
ten items or ten million.

#### Q3.3 — List vs set?
A set has no duplicates, no order, and answering "is this in here?" is instant.
With a list, Python has to walk through every item to check.

The rule: the moment you find yourself asking "is x in here?" repeatedly,
you want a set.

#### Q3.4 — Mutable vs immutable types?
Mutable means changeable: lists, dictionaries, sets. Immutable means fixed once
created: numbers, text, tuples. Fixed things are safe to share around, because
nobody can change them behind your back.

#### Q3.5 — Shallow vs deep copy?
A shallow copy makes a new outer box but the things inside are still the same
objects — change one and both "copies" change. A deep copy copies everything
all the way down, so the two are genuinely independent.

#### Q3.6 — What is a list comprehension?
A compact way of building a list in one line: `[x*x for x in nums if x > 0]`.
Shorter and faster than writing a loop that appends.

#### Q3.7 — Generator vs list?
A list builds everything up front and holds it all in memory. A generator
hands you one item at a time and forgets it afterwards, so memory stays flat
no matter how much data there is.

That's why you use one to read a huge file or a video stream — you'd never
fit it all in memory otherwise.

#### Q3.8 — What does `yield` do?
It pauses the function, hands one value back to whoever asked, and remembers
exactly where it stopped. Next time you ask for a value, it carries on from
there.

## Functions and structure

#### Q3.9 — What is a decorator?
A function that wraps another one to add behaviour without editing it — adding
logging, timing, or a login check. The `@app.get(...)` line in FastAPI is a
decorator.

#### Q3.10 — `*args` and `**kwargs`?
Ways of saying "accept however many extra arguments get passed." `*args`
collects the unnamed ones, `**kwargs` collects the named ones.

#### Q3.11 — What is the GIL?
A lock inside Python that means only one thread can run Python code at a time.

The practical consequence: threads help when your code is **waiting** for
something — a network call, a file, sending an email. They don't help when
your code is **calculating** something, because only one thread gets to run
anyway. For heavy calculation you need separate processes.

This is exactly why the threaded email alerts in your fire detector work.
Sending mail is waiting, not calculating.

#### Q3.12 — Multithreading vs multiprocessing?
Threads share memory and are cheap to create, but the lock above means they
only help with waiting. Processes each get their own memory and really do run
at the same time, so they help with calculation — but they cost more to start.

#### Q3.13 — `is` vs `==`?
`==` asks "are these two things equal?" `is` asks "are these literally the
same object in memory?" Only use `is` when checking for `None`.

#### Q3.14 — How does Python manage memory?
It counts how many things are pointing at each object, and throws an object
away when nothing points at it any more. There's also a cleanup pass for
objects that point at each other in a circle, which the counter alone can't
catch.

#### Q3.15 — What is a lambda?
A tiny unnamed function written in one line, usually passed straight to
something else: `sorted(d, key=lambda x: x[1])`.

#### Q3.16 — `map`, `filter`, `reduce`?
`map` runs a function over every item. `filter` keeps the items that pass a
test. `reduce` squashes the whole sequence down to one value. In practice a
comprehension is usually easier to read.

#### Q3.17 — What does `enumerate` give you?
The position and the item together, so you don't have to keep a counter
yourself: `for i, frame in enumerate(frames)`.

#### Q3.18 — What does `zip` do?
Pairs up items from two or more lists, side by side, stopping when the
shortest one runs out. `zip(boxes, labels)`.

## Errors, classes and files

#### Q3.19 — How do you handle exceptions?
`try` the risky thing, `except` the specific error you expect, and `finally`
for cleanup that must happen either way.

Catch the specific error, not everything. A bare `except` swallows real bugs
and you never find out.

#### Q3.20 — What is a context manager?
Something you use with `with`, which guarantees cleanup happens. `with open(f)
as fh:` closes the file even if the code inside crashes.

#### Q3.21 — What are the four pillars of object-oriented programming?
Keep an object's internals private (encapsulation). Build new classes on top
of old ones (inheritance). Let different classes respond to the same method
name in their own way (polymorphism). Show a simple interface and hide the
messy mechanics behind it (abstraction).

#### Q3.22 — `__init__` vs `__new__`?
`__new__` creates the object; `__init__` fills it in. You almost always only
ever write `__init__`.

#### Q3.23 — What is `self`?
The particular object the method was called on. Python passes it in as the
first argument, explicitly, rather than hiding it.

#### Q3.24 — Class method vs static method vs instance method?
An instance method works on one object and takes `self`. A class method works
on the class itself and is often used as an alternative way to build one. A
static method takes neither — it's just a plain function kept inside the class
for tidiness.

#### Q3.25 — Module vs package?
A module is one `.py` file. A package is a folder of them.

#### Q3.26 — What are virtual environments, and why use them?
A separate set of installed libraries for each project, so one project's
PyTorch version can't break another project. `venv`, `conda`, or `uv`.

#### Q3.27 — How do you read a large file without running out of memory?
Loop over it line by line rather than loading the whole thing:
`for line in open(path)`. For a big CSV, read it in chunks with
`pd.read_csv(..., chunksize=...)`.

#### Q3.28 — What is `if __name__ == "__main__"` for?
It runs that block only when you run the file directly, not when some other
file imports it. Without it, importing a module would fire off its script
behaviour as a side effect.

#### Q3.29 — What is type hinting, and does it slow anything down?
Notes in the code saying what type each argument should be. Python ignores
them when running, so there's no cost. Tools read them — which is how FastAPI
turns them into automatic request checking.

#### Q3.30 — `append` vs `extend`?
`append` adds one item. `extend` adds every item from a list, one by one.
`[1,2].append([3,4])` gives you `[1,2,[3,4]]`; `extend` gives you `[1,2,3,4]`.

:::practice One thing to rehearse
The GIL question (Q3.11) is the one most likely to come up and most likely to
be answered badly. Practise saying it in two sentences: only one thread runs
Python at a time, so threads help with waiting and not with calculating.
Then land it on your fire detector's email thread.
:::

:::recap
- Tuple, set and dictionary each exist for one reason — know which reason.
- A generator hands you one item at a time, which is why it handles files
  bigger than memory.
- The GIL means threads help with waiting, processes help with calculating.
- `is` is only for `None`.
- Catch specific exceptions, never a bare `except`.
- Where an answer can land on your own code, land it there.
:::

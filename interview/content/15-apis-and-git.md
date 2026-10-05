# APIs, Streamlit and Git
@short: APIs and Git
@subtitle: The plumbing round
@tier: core
@prereq: none
@blurb: FastAPI, Streamlit and Git are on your resume and all three appear in your projects, so these are fair game. Two of them --- where you load the model, and `def` versus `async def` --- are the questions that reveal whether you have actually served a model or only written one.
@objectives:
- Explain REST and the status codes you will be asked about
- Say where to load a model and why, without hesitating
- Answer the async question correctly, because most people get it wrong
- Describe a sensible Git workflow in one sentence

## REST and FastAPI

#### Q23.1 — What is a REST API?
A way for one program to ask another for something over the web. You send a
request to an address, you get a response back, usually as JSON.

#### Q23.2 — GET vs POST vs PUT vs DELETE?
GET fetches something and changes nothing. POST creates something or submits
data. PUT replaces something. DELETE removes it.

Model predictions use POST, because you're sending data in the body.

#### Q23.3 — What makes an API RESTful?
Addresses name things rather than actions (`/orders/42`, not
`/getOrder?id=42`), the right verb for the right job, and every request carries
everything needed — the server doesn't remember you between calls.

#### Q23.4 — Name the status codes you should know.
200 fine. 201 created. 400 your request was malformed. 401 you're not logged
in. 403 you're logged in but not allowed. 404 not found. 422 the data failed
validation. 429 you're sending too many. 500 we broke. 503 we're down.

The 401-versus-403 distinction gets asked: 401 is "who are you", 403 is "I know
who you are and no".

#### Q23.5 — What is FastAPI, and why choose it for ML serving?
A Python web framework that reads your type annotations and uses them to check
incoming requests automatically, and to generate interactive docs.

For serving a model that's three things nearly free: input validation, good
throughput, and a `/docs` page where anyone can try your model without writing
code.

#### Q23.6 — What is Pydantic doing in your API?
Defining the shape of what comes in and goes out, checking incoming JSON
against it, and rejecting anything wrong with a clear error **before** it
reaches your model.

#### Q23.7 — Why validate inputs at the API boundary for an ML service?
Because a model given nonsense doesn't crash — it returns a **confident wrong
number**. There's no error to catch.

Validation turns a silent failure into a loud one. That's the whole argument,
and it's specific to ML.

#### Q23.8 — What is ASGI? What is Uvicorn?
ASGI is the modern standard for how a Python web app talks to a web server,
supporting things that happen concurrently. Uvicorn is a server that
implements it and actually runs your app.

#### Q23.9 — `def` vs `async def` in FastAPI — which for model inference?
Use `async def` when you're **waiting** for something — a database, another
API.

Use plain `def` for model prediction, because that's **calculation**. FastAPI
automatically runs plain functions on a separate thread so they don't freeze
everything else.

Putting a blocking prediction inside `async def` is a classic mistake: it
blocks the main loop and your whole service stalls while one prediction runs.

#### Q23.10 — Where do you load the model — per request or at startup?
At startup, once.

Loading it per request adds seconds to every single call. Expect to be asked
this — it's a quick way to find out whether you've actually served a model.

#### Q23.11 — How do you handle concurrent requests to one model?
Run several worker processes, or queue requests and process them in batches.

Watch memory though — each worker loads its own copy of the weights. Four
workers means four copies.

#### Q23.12 — What is a health-check endpoint, and why does it matter?
A cheap `/health` address that returns OK when the service is up and the model
is loaded.

Load balancers and orchestrators call it to decide whether to send you
traffic. Without it, they'll happily route requests to a container that's still
starting up.

#### Q23.13 — How do you version an ML API?
Put the version in the address (`/v1/predict`) and return the **model**
version in the response.

That second part matters: it means any prediction can be traced back to
exactly which model made it, months later.

#### Q23.14 — What is CORS, and when does it bite you?
Browsers block a page on one address from calling a different address, unless
the server explicitly allows it.

It bites the moment your React dashboard on one port calls your FastAPI on
another — which is exactly SafeSight's setup.

#### Q23.15 — What is Streamlit, and what are its limits?
A library that turns a Python script into a web page, which is ideal for demos
and internal tools.

Limits: it re-runs the entire script every time anyone clicks anything, you
have limited control over layout, and it isn't built to be a real multi-user
front end.

#### Q23.16 — Why Streamlit for the UI but FastAPI for the model?
Separation. The API is reusable and testable on its own; Streamlit is just one
thing that happens to call it.

It also means the same model can serve the React dashboard, a script, or
anything else — without duplicating the logic.

#### Q23.17 — `st.cache_data` vs `st.cache_resource`?
`cache_data` for values you can copy — a loaded dataframe. `cache_resource`
for things there should only ever be one of — your model, a database
connection.

Without caching, Streamlit reloads your model on every single widget click,
because it re-runs the whole script.

#### Q23.18 — How do you secure a prediction endpoint?
An API key or token, HTTPS, rate limiting, a cap on input size, and no stack
traces in error responses — those leak your file paths and library versions.

#### Q23.19 — How would you stream LLM responses to a UI?
Send tokens as they're generated rather than waiting for the whole answer.

The total time doesn't change at all, but it **feels** far faster because
something appears immediately. Worth mentioning for DocuMind.

## Git

#### Q24.1 — What is Git, and what is GitHub?
Git tracks changes to your code and runs entirely on your machine. GitHub
hosts those repositories online and adds the collaboration layer — pull
requests, issues, automated builds.

#### Q24.2 — Explain the basic workflow.
Pull the latest. Make a branch. Edit. Stage. Commit. Push. Open a pull
request. Get it reviewed. Merge.

#### Q24.3 — `git fetch` vs `git pull`?
Fetch downloads what's changed but doesn't touch your files. Pull does both —
downloads and merges it in.

Fetch first if you want to see what's coming before accepting it.

#### Q24.4 — Merge vs rebase?
Merge keeps both histories and adds a commit joining them. Rebase replays your
commits on top of the other branch so the history looks like a straight line.

The rule: never rebase a branch other people are working on. You'd be
rewriting history they already have.

#### Q24.5 — What is a merge conflict, and how do you resolve one?
Two branches changed the same lines, so Git can't decide which is right. It
marks both versions in the file; you edit it to what it should actually be,
then stage and commit.

#### Q24.6 — `git reset` vs `git revert`?
Reset rewinds history — only safe on commits nobody else has.

Revert adds a **new** commit that undoes an old one, leaving history intact.
That's the safe one on a shared branch.

#### Q24.7 — What is `.gitignore`, and what belongs in it for ML?
A list of things Git should ignore. For ML: virtual environments, cache
folders, your `.env` file, datasets, and model weights.

#### Q24.8 — Should model weights and datasets live in Git?
No. Git keeps a complete copy of every version of every file forever, so a few
rounds of a 200 MB model makes the repository enormous — permanently. Deleting
it later doesn't shrink it.

Use Git LFS, DVC, or just store them elsewhere and keep a reference.

#### Q24.9 — What is a pull request, and what makes a good one?
A request to merge your branch, with a chance for someone to review it first.

A good one is small, does one thing, and explains **why** rather than just
what. A 2,000-line pull request doesn't get reviewed, it gets approved.

#### Q24.10 — What is a good commit message?
A short imperative summary, then a blank line, then the reasoning if it needs
one.

"Fix NMS threshold merging adjacent worker boxes" beats "update". In six
months that message is the only explanation anyone has.

#### Q24.11 — What is `git stash`?
Puts your half-finished changes aside so you can switch branches, then lets
you bring them back.

#### Q24.12 — How do you find which commit broke something?
`git bisect`. You tell it a commit that worked and one that doesn't, and it
does a binary search — checking out the midpoint, you say better or worse, and
it narrows down.

Three hundred commits takes about nine checks instead of reading three hundred
diffs.

:::practice The two that catch people
Q23.9 and Q23.10 — async versus plain, and where you load the model. Both are
one sentence, both are asked constantly, and both reveal immediately whether
you've actually served a model or only trained one.
:::

:::recap
- 401 is "who are you", 403 is "I know and no".
- Validate at the API boundary, because a model given nonsense returns a
  confident wrong number rather than an error.
- Plain `def` for prediction, `async def` for waiting.
- Load the model once at startup.
- Return the model version with every prediction so it can be traced.
- Never rebase a shared branch; revert rather than reset on one.
- Model weights never belong in Git.
:::

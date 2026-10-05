# MLOps: MLflow, Docker and CI/CD
@short: MLOps
@subtitle: Your churn project is the evidence, so know every piece of it
@tier: core
@prereq: none
@blurb: This is where your churn project earns its place. The model is weak and the pipeline is strong, so lead with the pipeline. Two questions here are about your own stale README --- have the honest answer ready, and fix the README before anyone reads it.
@objectives:
- Explain why ML is harder to deploy than normal software
- Walk through your Dockerfile and justify the line order
- Describe what your CI pipeline actually does, without inflating it
- Say how you would detect a model going wrong in production

## The idea

#### Q22.1 — What is MLOps?
Applying normal software engineering discipline to machine learning: versioned
data and models, training you can repeat and get the same answer, automated
testing and deployment, and watching it once it's live.

#### Q22.2 — Why is ML harder to deploy than normal software?
Three reasons.

Normal code does the same thing forever; a model's behaviour depends on data,
so you have to version the data too. Models get worse over time as the world
changes, even though the code never changed. And correctness isn't yes/no —
it's a number that can drift.

#### Q22.3 — What is MLflow, and which parts have you used?
A tool for recording experiments and managing models. You log what settings
you used, what score you got, and the model file itself — so six weeks later
you can find out exactly what produced the thing currently running.

You used the tracking part plus automatic promotion of the best run.

#### Q22.4 — Run vs experiment in MLflow?
An experiment is a named group — "churn model". A run is one execution inside
it, with its own settings, scores and saved files.

#### Q22.5 — How does your automatic best-run promotion work?
It looks through the recorded runs, compares them on the logged score, and
marks the winner as the one to serve.

Then volunteer the weakness: **the logged score is accuracy.** So it can
promote a model that's actually worse at catching churners. Naming your own
design flaw is far more impressive than hoping they don't spot it.

#### Q22.6 — What is a model registry?
Versioned storage for models with stages — staging, production, archived. So
your deployment points at "whatever is in production" rather than a file path
that someone has to remember to update.

#### Q22.7 — Why log parameters and metrics rather than keep a spreadsheet?
Because in six weeks you'll need to know exactly which settings produced the
model currently serving traffic, and a spreadsheet will be out of date or
missing.

## Docker

#### Q22.8 — What is Docker, and what problem does it solve?
It packages your code, its libraries and its runtime into one image that runs
identically anywhere. It kills "it works on my machine."

#### Q22.9 — Container vs virtual machine?
A virtual machine simulates an entire computer including its own operating
system — gigabytes, slow to start.

A container shares the host's operating system and just isolates your
application — megabytes, starts in seconds.

#### Q22.10 — Image vs container?
The image is the recipe. The container is the thing actually running. One
image, many containers.

#### Q22.11 — Walk me through your Dockerfile.
Start from a Python base image. Set the working directory. Copy
`requirements.txt`. Install the dependencies. **Then** copy the source code.
Expose the port. Set the command to run.

Know why the requirements come before the source — it's the next question and
it's a favourite.

#### Q22.12 — Why copy requirements before the application code?
Because Docker caches each step. Dependencies change rarely; your code changes
constantly.

Copy requirements first and install, and then a code change only rebuilds the
last step — a few seconds. Copy everything at once and every one-character
edit reinstalls PyTorch from scratch.

This is one of the most-asked Docker questions there is.

#### Q22.13 — What is a multi-stage build, and why for ML?
Build in a big image that has all the compilers, then copy only the finished
result into a small clean image.

ML images bloat quickly — the build tools alone can be hundreds of megabytes.
This strips all of that out of what you actually ship.

#### Q22.14 — What is Docker Compose, and what does it give your churn project?
A single file describing several containers and how they connect, so one
command starts everything.

For your project it means a reviewer runs `docker compose up` and gets the API
and the UI running together. That's a real advantage when someone is assessing
your work.

#### Q22.15 — How do containers talk to each other in Compose?
By service name on a shared network. So the UI calls `http://api:8000`, not
`localhost` — because inside a container, `localhost` means that container
itself.

#### Q22.16 — What is a volume, and why does it matter for models?
Storage that lives outside the container and survives restarts.

It matters because model weights and your MLflow data must be on a volume.
Otherwise every restart wipes them.

#### Q22.17 — How do you keep secrets out of an image?
Environment variables, a `.env` file excluded from Git, or a proper secrets
manager.

Never bake a key into the image. Even if a later step deletes it, it's still
sitting in the image's history where anyone can read it. Directly relevant to
your SMTP credentials.

#### Q22.18 — What is `.dockerignore` for?
Keeping junk out of the build — the `.git` folder, datasets, virtual
environments. Smaller build context means faster builds and smaller images.

#### Q22.19 — What is Kubernetes, and would your project need it?
It runs containers across many machines, handling scaling and restarting
things that crash.

Honest answer: **no**, a single-service demo doesn't need it. Knowing when not
to reach for something is a point in your favour, not against you.

## CI/CD

#### Q22.20 — What is CI/CD?
Continuous Integration: every time you push code, it gets built and tested
automatically. Continuous Delivery: if it passes, it gets released
automatically.

#### Q22.21 — What does your GitHub Actions pipeline actually do?
Runs import checks and builds the Docker image on push.

Describe it exactly. It's modest, and overstating it is much worse than its
actual size — because the follow-up question will expose it.

#### Q22.22 — Your README says CI/CD is future work but the workflow exists. Explain.
"The workflow is real, the README is out of date."

Then fix it. And check the workflow triggers on the branch you actually use —
if it's set to `main` and your branch is `master`, it has never run once, and
finding that out live is painful.

#### Q22.23 — What is a GitHub Actions workflow made of?
A YAML file with three parts: when to run (on push, on pull request), what
machine to run on, and the list of steps.

#### Q22.24 — What would you add to your CI pipeline next?
Real unit tests. Linting. A check that the data has the expected columns. A
smoke test that actually calls `/predict` in the built container. And a
minimum-score gate that fails the build if the model gets worse.

Having this list ready turns a thin pipeline into evidence of judgement.
You're showing you know what good looks like even if you haven't built it yet.

## Monitoring

#### Q22.25 — What is model drift? Data drift vs concept drift?
**Data drift**: the incoming data changes. Your customers are now younger than
the ones you trained on.

**Concept drift**: the relationship changes. The same customer profile now
means something different because a competitor launched.

Both make a model worse without any code changing.

#### Q22.26 — How do you detect drift without labels?
You usually don't get to know the right answer for months, so you watch the
inputs and the outputs instead.

Compare the distribution of incoming features against what you trained on, and
watch the distribution of predictions. If the model suddenly starts predicting
churn twice as often, something has changed — even before you know whether
it's right.

#### Q22.27 — How do you monitor a model in production?
Four layers, in order of how quickly they tell you something.

Operational: is it up, how fast, how many errors. Data quality: missing
fields, impossible values, categories you've never seen. Prediction
distribution: has the output shifted. And finally accuracy, once the real
answers eventually arrive.

#### Q22.28 — Shadow deployment, canary, blue-green?
**Shadow**: the new model sees real traffic but its answers aren't used.
Zero risk, and you can compare it to the old one on identical inputs.

**Canary**: a small slice of real traffic goes to the new model.

**Blue-green**: two complete environments, and you flip a switch.

All three are about limiting how much damage a bad model can do.

#### Q22.29 — What is A/B testing a model?
Splitting real traffic between two models and comparing a **business** outcome
— retained customers, not offline accuracy. With enough traffic to tell a real
difference from noise.

#### Q22.30 — How often would you retrain the churn model?
Trigger-based rather than on a calendar: retrain when the data has drifted
past a threshold, or when recall drops.

If you have no monitoring yet, monthly is a reasonable default — but say that
it's a default, not a decision.

#### Q22.31 — What is reproducibility, and how do you achieve it?
Same inputs give the same model. Pin your library versions, set the random
seeds, version the data, log everything, and containerise the environment.

Miss any one and you get a model you can't recreate.

#### Q22.32 — What is a feature store, and would you need one?
A central place where computed features live, so training and serving both use
exactly the same calculation.

Would you need one? No — it's for when several models and teams share
features. For one project it's overkill, and saying so shows judgement.

#### Q22.33 — What is training-serving skew?
When the way you compute a feature in training differs from how you compute it
when serving. The model gets inputs that don't look like what it learned from,
and quietly gets worse.

Your protection is that the scaler and encoders ship **inside** the saved
pipeline, so both paths run identical code.

:::practice Before the interview
Open your `ci.yml` and check the branch it triggers on. Then open both stale
READMEs and fix them. That is an hour's work and it closes two of the most
uncomfortable questions in this chapter.
:::

:::recap
- ML is harder to deploy because behaviour depends on data, and models decay
  while code doesn't.
- Copy requirements before source in a Dockerfile — layer caching. Most-asked
  Docker question.
- Name your MLflow promotion flaw yourself: it promotes on accuracy.
- `localhost` inside a container means that container — use service names.
- Never bake secrets into an image; they stay in the history.
- "No, we don't need Kubernetes" is a good answer.
- Watch inputs and prediction distributions, because real labels arrive late.
:::

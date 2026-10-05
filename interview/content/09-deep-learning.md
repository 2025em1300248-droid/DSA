# Deep Learning
@short: Deep Learning
@subtitle: From the forward pass to the training loop
@tier: core
@prereq: Chapter 7
@blurb: You list PyTorch, so expect the whole chain: what a network is, what the loss does, how the gradients get back, and what the optimiser does with them. Then the practical PyTorch questions, which are where interviewers find out whether you have actually trained anything.
@objectives:
- Explain a neural network and backpropagation without equations
- Say why activation functions exist in one sentence
- Answer the PyTorch traps: zero_grad, eval mode, no_grad
- Write a training loop from memory

## What a network is

#### Q12.1 — What is a neural network, in one sentence?
Layers of simple calculations stacked up, where each layer's output feeds the
next, and all the numbers inside get nudged repeatedly until the output is
close to what you wanted.

#### Q12.2 — What is a perceptron?
A single unit: multiply each input by a weight, add them up, add a bias, push
the result through a simple function. On its own it can only separate things
that a straight line can separate.

#### Q12.3 — Why do we need activation functions at all?
Without them, stacking layers is pointless — a stack of straight-line
operations is still just one straight line. The bend is what lets depth buy
you anything.

#### Q12.4 — Compare sigmoid, tanh and ReLU.
Sigmoid squashes everything into 0 to 1, but at the extremes it flattens out
and learning stops. Tanh is the same idea centred on zero instead, with the
same flattening problem.

ReLU just sets negatives to zero and leaves positives alone. It's cheap, it
doesn't flatten out for positive values, and it's the default for hidden
layers.

#### Q12.5 — What is the dying ReLU problem, and the fix?
If a unit's input goes negative and stays negative, it outputs zero forever
and never learns again — it's dead.

Fix: use a version that lets a small signal through for negatives instead of
zero. LeakyReLU, ELU or GELU.

#### Q12.6 — What is softmax?
Turns a set of scores into probabilities that add up to 1. It's what you put
on the output when you're picking one class out of several.

#### Q12.7 — When do you use sigmoid instead of softmax on the output?
When the classes aren't mutually exclusive — something can be several things
at once.

Which is exactly your PPE case: one worker can be missing a helmet **and**
gloves. Softmax would force them to compete; sigmoid lets each be judged
independently.

#### Q12.8 — What is a loss function? Name the ones you'd use.
A single number saying how wrong the model currently is. Training is just
making that number smaller.

Cross-entropy for classification. Mean squared error for predicting numbers.
YOLO uses a combination — one part for the box position, one for the class.

#### Q12.9 — Explain forward and backward propagation.
Forward: the input flows through the layers and comes out as a prediction,
which gets compared to the answer to give a loss.

Backward: that error gets traced back through the layers, working out how much
each weight contributed to it, so each one knows which way to move.

#### Q12.10 — What is gradient descent? Batch vs stochastic vs mini-batch?
Nudge every weight slightly in the direction that reduces the error. Repeat.

Batch uses all your data for each nudge — accurate but slow. Stochastic uses
one example — fast but jumpy. Mini-batch uses 32 to 256 and is what everybody
actually does.

#### Q12.11 — What is the learning rate, and what happens if it's wrong?
How big each nudge is.

Too big and the model overshoots and the error bounces around or blows up.
Too small and it takes forever, or gets stuck somewhere mediocre.

#### Q12.12 — What is a learning-rate schedule? Name two.
Reducing the step size as training goes on — big steps early to get roughly
there, small steps later to settle in.

Step decay cuts it at fixed points. Cosine decay reduces it smoothly.
Transformers usually also warm up at the start.

#### Q12.13 — Compare SGD, momentum, RMSprop and Adam.
SGD is the plain version. Momentum remembers which direction it's been going
and keeps rolling that way, which helps it push through noise. RMSprop gives
each weight its own step size based on how big its recent nudges were. Adam
does both, and it's the default.

#### Q12.14 — What is the vanishing gradient problem?
As the error signal travels back through many layers, it gets multiplied by
small numbers over and over until it's effectively zero — so the early layers
stop learning entirely.

Fixed with ReLU, normalisation, and skip connections that give the signal a
shortcut back.

#### Q12.15 — What is exploding gradient, and the fix?
The opposite — the signal gets multiplied up until the weights blow up and you
get `NaN`. Fix by capping the size of the update. One line of code.

#### Q12.16 — What is batch normalisation, and why does it help?
It rescales each layer's inputs so they stay in a sensible range instead of
drifting as training progresses. Training becomes faster and much more stable.

#### Q12.17 — Batch norm vs layer norm — which does a transformer use?
Batch norm normalises across all the examples in the batch. Layer norm
normalises within one example, across its features.

Transformers use layer norm, because sentence lengths and batch sizes vary and
batch norm doesn't cope well with that.

#### Q12.18 — What is dropout? Does it run at inference?
During training, randomly switch off a fraction of the units each step. That
stops the network leaning on any single one and forces it to spread the work.

It's switched off at prediction time — which is exactly what `model.eval()`
does.

#### Q12.19 — What is early stopping?
Stop training when the validation score stops improving, and keep the best
version you saw. It's the cheapest way to prevent overfitting there is.

#### Q12.20 — What is weight initialisation, and why not use zeros?
Starting all weights at zero means every unit in a layer computes exactly the
same thing and receives exactly the same update — so they never become
different from each other and the layer is useless.

So you start with small random values, scaled to suit your activation
function.

#### Q12.21 — Epoch vs batch vs iteration?
An epoch is one full pass over all your data. A batch is one group of examples.
An iteration is one weight update, which is one batch.

#### Q12.22 — How do you pick batch size?
The biggest that fits in your GPU memory and still trains well. Bigger is
faster per epoch but sometimes generalises slightly worse, and may need a
higher learning rate to compensate.

## PyTorch in practice

#### Q12.23 — What is transfer learning? Why does it matter for all your projects?
Start from a model already trained on a huge dataset, then adapt it to yours.

It's the entire reason you could train a fire detector or a five-class PPE
model on a modest custom dataset. The pretrained model already knows what
edges, textures and object shapes look like — you're only teaching it your
specific objects.

#### Q12.24 — Fine-tuning vs feature extraction?
Feature extraction: freeze the pretrained part completely and train only the
new output layer. Fine-tuning: unfreeze some or all of it and train gently at
a low learning rate.

Freeze more when you have less data.

#### Q12.25 — What is data augmentation? Which are safe for PPE detection?
Making extra training examples by altering the ones you have — flipping,
rotating, changing brightness.

Safe for your case: horizontal flip, scaling, brightness and contrast, slight
rotation.

**Risky**: flipping vertically, because workers aren't upside down. And
aggressive colour shifts, because a high-vis vest is **defined** by its
colour — shift it and you've destroyed the signal.

#### Q12.26 — What is a hyperparameter you tuned, and how?
Have a real one ready. Input resolution, confidence threshold, learning rate
or number of epochs — tuned by watching the validation score. Name the number
you watched.

#### Q12.27 — Tensor vs NumPy array?
A tensor can live on a GPU, and it remembers the operations done to it so
gradients can be computed. Otherwise the two are deliberately very similar.

#### Q12.28 — What is autograd in PyTorch?
It quietly records every operation you do, building a map of how the result
was computed. Then `loss.backward()` walks that map backwards and works out
every gradient for you.

#### Q12.29 — What does `optimizer.zero_grad()` do, and what breaks without it?
PyTorch **adds** new gradients to the old ones rather than replacing them. So
if you don't clear them each step, you're updating with the sum of every batch
so far and the model trains wrongly.

Classic interview trap. Know this one.

#### Q12.30 — Write a minimal PyTorch training loop.
```python
for xb, yb in loader:
    optimizer.zero_grad()
    out = model(xb)
    loss = criterion(out, yb)
    loss.backward()
    optimizer.step()
```
Be able to write this from memory. Five lines: clear, predict, score,
blame, update.

#### Q12.31 — `model.train()` vs `model.eval()`?
They switch dropout and batch norm between their training and prediction
behaviour. Forgetting `eval()` when predicting means dropout is still randomly
switching units off, so you get different answers each time you run it.

#### Q12.32 — What does `torch.no_grad()` do?
Tells PyTorch to stop recording operations, because you're not going to train
on this. Less memory, faster. Wrap your whole prediction path in it.

#### Q12.33 — PyTorch vs TensorFlow?
PyTorch feels like ordinary Python and you can step through it with a
debugger, which is why research moved to it. TensorFlow has a longer history
on the deployment side.

Say you use PyTorch and can read Keras. That's the honest answer.

#### Q12.34 — What is a Dataset and a DataLoader?
A Dataset knows how to fetch one example by number. A DataLoader wraps it and
handles batching, shuffling, and loading in parallel while the GPU works.

#### Q12.35 — How do you save and load a model?
Save the weights (`state_dict`), not the whole Python object. Then build the
same architecture and load the weights into it.

Saving the whole object ties the file to your exact code layout, and it breaks
the moment you move a file.

#### Q12.36 — What is mixed-precision training?
Doing most of the arithmetic in half precision while keeping a full-precision
master copy of the weights. Roughly halves memory and speeds things up, with
almost no accuracy cost on modern GPUs.

#### Q12.37 — Why do we train on GPUs?
Because training is thousands of independent multiplications happening at
once, and a GPU has thousands of small cores to do them simultaneously. A CPU
has a handful of fast ones, which is the wrong shape for this job.

#### Q12.38 — Your model trains fine but inference is slow. What do you do?
Measure first, to find out whether it's the model or the preprocessing around
it.

Then: batch the requests, make sure you're in eval mode with gradients off,
export to a faster runtime, reduce the number precision, lower the input
resolution, or use a smaller model variant.

:::practice The three traps
`zero_grad`, `model.eval()` and `no_grad()`. All three are asked constantly,
all three are one-sentence answers, and all three catch people who have copied
a training loop without understanding it.
:::

:::recap
- Activation functions are what make depth worth anything.
- Sigmoid on the output for PPE, because a worker can be missing two things at
  once.
- Backprop traces the error back to find out which weight is responsible.
- PyTorch adds gradients rather than replacing them — hence `zero_grad`.
- Transfer learning is why your small datasets worked at all.
- Don't flip PPE footage vertically, and don't shift the colours — the vest is
  defined by its colour.
:::

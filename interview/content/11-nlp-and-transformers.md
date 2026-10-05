# NLP and Transformers
@short: NLP and Transformers
@subtitle: How a language model actually works
@tier: core
@prereq: Chapter 9
@blurb: You list LLMs, Llama 3 and Ollama, so they will ask how a transformer works. The attention answer is the one that matters --- get it right in plain words and the rest of the section goes easily. The older NLP material underneath it still gets asked because it is the floor your RAG projects stand on.
@objectives:
- Explain attention without writing the formula
- Say what query, key and value mean in ordinary words
- Describe how an LLM is trained and what fine-tuning changes
- Answer the hallucination question honestly

## Classic NLP

#### Q16.1 — What is tokenisation?
Chopping text into the pieces a model actually reads. Sometimes whole words,
usually chunks of words.

#### Q16.2 — What is subword tokenisation, and why do LLMs use it?
Common words stay whole; rare words get broken into familiar pieces.
"Unhappiness" might become "un", "happi", "ness".

Why: it keeps the vocabulary small, and the model never meets a word it can't
represent at all — worst case it spells it out in pieces.

#### Q16.3 — What are stemming and lemmatisation?
Both cut words back to a root so "running" and "runs" count as the same thing.

Stemming chops crudely and can produce non-words — "studies" becomes "studi".
Lemmatisation uses a dictionary and gives you a real word — "studies" becomes
"study".

#### Q16.4 — What are stop words? Should you always remove them?
Very common words like "the", "is", "and".

Remove them for simple word-counting models, where they're just noise. Keep
them for transformers, where the grammar genuinely carries meaning.

#### Q16.5 — What is bag of words?
Representing a document by which words appear and how often, completely
ignoring the order. Crude, but surprisingly effective for classification.

#### Q16.6 — What is TF-IDF?
A way of scoring words that rewards being frequent in **this** document but
rare across all documents. So "the" scores near zero and "defibrillator"
scores high.

#### Q16.7 — What are n-grams?
Short runs of consecutive words. They recover a little of the word order that
bag-of-words throws away — "not good" stays distinguishable from "good".

#### Q16.8 — What are word embeddings? Name two methods.
Turning each word into a list of numbers, arranged so that words with similar
meanings end up close together. Word2Vec and GloVe.

#### Q16.9 — Word2Vec: CBOW vs skip-gram?
CBOW guesses a word from the words around it. Skip-gram does the reverse —
guesses the surroundings from the word. Skip-gram handles rare words better.

#### Q16.10 — What's the limitation of Word2Vec that transformers solved?
One fixed vector per word, forever. So "bank" has a single meaning, whether
you mean money or a river.

Transformers produce a different vector depending on the sentence, so "bank"
means different things in different contexts.

#### Q16.11 — What is named entity recognition?
Picking out and labelling the people, companies, places and dates in text.
Useful in document question-answering for pulling structured facts out.

#### Q16.12 — What is POS tagging?
Labelling each word with its part of speech — noun, verb, adjective.

#### Q16.13 — What is an RNN, and what's its problem?
It reads a sequence one item at a time, carrying a running memory.

Two problems: it has to go in order, so it can't be parallelised and is slow.
And the memory fades, so by the end of a long sentence it has forgotten the
beginning.

#### Q16.14 — How do LSTM and GRU help?
They add gates that decide what to keep, what to forget and what to pass on.
That lets information survive much longer. GRU is a lighter version with fewer
gates.

#### Q16.15 — What is seq2seq, and why was attention added?
One network reads the input and squeezes it into a single summary; another
reads that summary and produces the output.

Attention was added because a single fixed summary can't hold a long sentence.
Instead of one summary, the output side gets to look back at **every** part of
the input and decide what's relevant right now.

#### Q16.16 — Text classification vs sentiment vs NER — in terms of output shape?
Classification and sentiment: one label for the whole document. NER: one label
per word.

Knowing the output shape is how you decide what to put on top of the model.

#### Q16.17 — What is cosine similarity, and why use it over distance for text?
It measures the angle between two vectors, ignoring how long they are.

For text that matters: a long document and a short one about the same topic
should count as similar. Using straight-line distance would say they're far
apart just because one has more words. It's what your FAISS search uses.

## Transformers

#### Q17.1 — What is a transformer?
A design where every word in a sentence can look directly at every other word,
all at once, instead of reading left to right.

That's what makes it fast to train — the whole sentence is processed in
parallel rather than one word at a time.

#### Q17.2 — What is self-attention, in plain terms?
Each word looks at every other word in the sentence and decides how much each
one matters to it. Then it builds a new version of itself that's blended from
the words it cared about.

So in "the cat sat on the mat because it was tired", the word "it" can look
back, notice "cat" is the relevant word, and take meaning from it.

#### Q17.3 — Explain query, key and value.
Think of it as a search.

Each word puts out a **query** — "here's what I'm looking for". Each word also
offers a **key** — "here's what I am". The query is compared against every key
to see which match. Then each word contributes its **value** — "here's what I
actually give you" — weighted by how well it matched.

#### Q17.4 — Give the attention formula.
Compare every query against every key, scale the result down, turn it into
percentages with softmax, and use those percentages to blend the values.

Written out: `softmax(QKᵀ / √d) V`. The division stops the numbers getting so
large that softmax picks one word and ignores everything else.

#### Q17.5 — What is multi-head attention for?
Running several attention calculations side by side, so different ones can
track different relationships — one might follow grammar, another might track
which pronoun refers to which noun. Then the results get combined.

#### Q17.6 — Why do transformers need positional encoding?
Because attention has no sense of order — to it, a sentence is just a bag of
words all looking at each other. So you have to explicitly add information
about where each word sits.

Modern models like Llama use rotary encoding, which handles relative distance
particularly well.

#### Q17.7 — Encoder-only vs decoder-only vs encoder-decoder?
Encoder-only reads and understands — BERT, and the embedding models you use
for search. Decoder-only generates text — GPT, Llama. Encoder-decoder reads
one thing and writes another — translation, the T5 family.

#### Q17.8 — What is causal or masked attention?
In a model that generates text, each word is only allowed to look **backwards**
at earlier words. Otherwise it could see the answer it's supposed to be
predicting, and it would learn nothing.

#### Q17.9 — What is the feed-forward layer doing in a transformer block?
Attention moves information **between** words. The feed-forward layer then
processes each word on its own.

It's also where most of the model's parameters are, which is roughly where its
stored knowledge lives.

#### Q17.10 — How is an LLM pretrained?
By covering up the next word and asking it to guess, over an enormous amount
of text. No human labelling needed — the text is its own answer key.

#### Q17.11 — Difference between pretraining, fine-tuning and RLHF?
Pretraining teaches it language in general, from scratch, at huge scale.
Fine-tuning adapts that general model to your specific task or style. RLHF
nudges it towards answers people actually prefer, using human comparisons.

#### Q17.12 — What is instruction tuning?
Training on pairs of "here's a request" and "here's a good response", so the
model follows instructions instead of just continuing your text.

It's the difference between a base model and a chat model.

#### Q17.13 — What is a context window, and why does it constrain your RAG design?
The maximum amount of text the model can hold at once.

It's exactly why you chunk documents and only retrieve the best few passages
rather than pasting in a whole PDF. The PDF wouldn't fit, and even if it did
you'd be paying for all of it.

#### Q17.14 — Why is attention expensive for long contexts?
Because every word looks at every other word. Double the length and you've
quadrupled the work. That's what all the "efficient attention" research exists
to fix.

#### Q17.15 — What is temperature? Top-k and top-p?
Temperature controls how adventurous the model is. Near zero it always picks
the most likely next word. Higher and it takes more risks.

Top-k limits it to the k most likely words. Top-p limits it to the shortest
list of words that covers a given share of the probability.

#### Q17.16 — What temperature for document QA, and why?
Near zero. In DocuMind you want it to faithfully report what the document
says. Creativity is a defect here, not a feature.

#### Q17.17 — What is a hallucination? Why do they happen?
A confident, fluent, completely wrong answer.

They happen because the model is trained to produce text that **sounds** right,
not text that **is** right. It has no internal sense of "I don't actually know
this."

#### Q17.18 — How do you reduce hallucination?
Give it the source material and tell it to answer only from that. Make it cite
which passage it used. Explicitly tell it to say "not found" rather than
guess. Set temperature near zero. Then check the citations actually resolve.

Your citation design in DocuMind is exactly this.

#### Q17.19 — What is LoRA? What is QLoRA?
Normally fine-tuning means updating billions of weights. LoRA freezes them all
and trains a tiny set of extra ones alongside — a fraction of a percent of the
model, with nearly the same effect.

QLoRA does the same but also stores the frozen model in a compressed form, so
a large model fits on one consumer GPU.

#### Q17.20 — What is PEFT?
The general name for this family — fine-tuning by changing a small number of
parameters rather than all of them. LoRA is the best-known member.

#### Q17.21 — When do you fine-tune vs use RAG vs just prompt?
Prompt first, always — it's free and takes minutes.

RAG when the problem is **missing or changing knowledge** — the model doesn't
know your documents.

Fine-tune when the problem is **behaviour** — it knows the material but won't
produce the format or tone you need consistently.

They solve different problems, and you can use both together.

#### Q17.22 — What is quantisation for LLMs? What does Ollama use?
Storing the model's numbers at lower precision so it fits on smaller hardware.
Ollama serves models in a compressed format — which is how you ran Llama 3 on
your own machine.

#### Q17.23 — What is Ollama, and why did you choose it?
A tool that downloads and runs language models locally, behind a simple API.

Why you chose it: no per-token bill, and no document ever leaves the machine.
Lead with the privacy argument — for confidential documents it's the strong
one.

#### Q17.24 — Open-source vs API models — how do you choose?
Open models when you need privacy, predictable cost, or offline operation.
Hosted APIs when you need the strongest possible model and don't want to run
anything.

For documents containing confidential material, local wins.

#### Q17.25 — What is a token, roughly how many words?
A chunk of a word. In English roughly three-quarters of a word on average, so
a thousand tokens is about seven hundred and fifty words.

#### Q17.26 — What is KV caching?
When generating text, the model would otherwise redo the work for every
previous word each time it adds a new one. Caching stores that work so each
new word only costs the new work.

It's the main reason generation speeds up after the first word.

#### Q17.27 — What is a mixture of experts?
Instead of one big network, you have many smaller specialist networks and a
router that picks a couple for each word.

So the model can hold far more knowledge without every word costing more to
compute.

#### Q17.28 — What is chain-of-thought prompting?
Asking the model to work through its reasoning step by step before answering.
It measurably improves anything with multiple steps.

#### Q17.29 — What are the risks of putting an LLM in a safety product?
Four. It can confidently cite a rule that doesn't exist. Instructions hidden
in an ingested document can hijack it. The model can be updated underneath you
and change behaviour silently. And operators can start trusting it more than
they should.

For SafeSight the honest answer is that the LLM **explains and cites** — a
human still signs off on anything being enforced. Saying that unprompted is a
strong signal.

:::practice The answer that carries this chapter
Q17.2, self-attention. Practise the "the cat... because it was tired" example
out loud. If you can explain attention with a sentence rather than a formula,
every other question in this chapter becomes easy.
:::

:::recap
- Attention means every word looks at every other word and decides what
  matters.
- Query is what I'm looking for, key is what I am, value is what I give you.
- Positional encoding exists because attention has no sense of order.
- Hallucinations happen because the model optimises for sounding right, not
  being right.
- Prompt first, RAG for missing knowledge, fine-tune for stubborn behaviour.
- Ollama's selling point for DocuMind is privacy — lead with that.
- For a safety product, say plainly that the LLM assists and a human decides.
:::

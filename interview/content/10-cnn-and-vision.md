# CNNs, YOLO and OpenCV
@short: CNNs and Vision
@subtitle: Your strongest area, and the one they will push hardest
@tier: core
@prereq: Chapter 9
@blurb: This is where your best project lives, so expect the longest and most detailed questioning here. Know how YOLO works, not just how to call it --- the difference shows immediately. The video-splitting question in this chapter is the one a sharp interviewer will use to find out whether you really understand your own evaluation.
@objectives:
- Explain convolution, pooling and receptive field in plain words
- Describe how YOLO works and why you chose it
- Answer the v5-versus-v8 question properly
- Know the one video-splitting mistake that invalidates a score

## Convolutional networks

#### Q13.1 — Why a CNN instead of a fully connected net for images?
Two reasons. A fully connected layer on a 640×640 image needs an enormous
number of weights. And it would have to learn separately that a helmet in the
top-left and a helmet in the bottom-right are both helmets.

A convolution slides the same small detector across the whole image, so it
learns "helmet" once and finds it anywhere, with far fewer weights.

#### Q13.2 — What is a convolution operation?
A small window slides across the image, and at each position it multiplies
what it sees by a set of learned numbers and adds them up. The result is a map
showing where that particular pattern appeared.

#### Q13.3 — What is a filter, and what does it learn?
The set of numbers in that window. Early layers learn simple things — edges,
colour changes. Middle layers combine those into textures and shapes. Deep
layers combine those into whole objects.

#### Q13.4 — What are stride and padding?
Stride is how far the window jumps each step. A bigger stride means a smaller
output. Padding adds a border of zeros around the edge so the output can stay
the same size as the input.

#### Q13.5 — Give the output-size formula.
`out = floor((in − kernel + 2×padding) / stride) + 1`.

Expect to compute this on a whiteboard. Practise it once with real numbers.

#### Q13.6 — What is pooling? Max vs average?
Shrinking the map by summarising each small patch into one number.

Max pooling keeps the strongest response, which is what you want when asking
"is this thing present anywhere here?" Average pooling smooths. Both make the
network slightly less fussy about exact position.

#### Q13.7 — What is a receptive field?
How much of the original image one unit deep in the network can actually
"see". It starts tiny and grows with depth — which is how deep layers end up
recognising whole objects rather than edges.

#### Q13.8 — What is a 1×1 convolution for?
Mixing and reducing the number of channels cheaply, without looking at
neighbouring pixels at all. Used everywhere to keep models small.

#### Q13.9 — What is a residual or skip connection?
Adding a layer's input to its output, so the layer only has to learn the
**difference** rather than the whole thing.

It also gives the error signal a shortcut straight back during training, which
is what made very deep networks trainable at all.

#### Q13.10 — Why are deeper networks hard to train?
The error signal fades as it travels back, so early layers barely learn. And
counterintuitively, adding layers can make accuracy worse. Skip connections
and normalisation are what fixed both.

#### Q13.11 — What is global average pooling, and why use it over flatten?
Instead of unrolling the whole feature map into a huge list, you just average
each channel down to one number. Far fewer weights, and it works with
different input sizes.

#### Q13.12 — Name some classic CNN architectures and what each contributed.
LeNet proved the idea. AlexNet added ReLU and GPUs. VGG showed that stacking
simple 3×3 layers works. Inception used several filter sizes in parallel.
ResNet introduced skip connections. MobileNet made them small enough for
phones.

#### Q13.13 — What is a depthwise separable convolution?
Splitting the work in two: first look at each channel's spatial pattern
separately, then mix the channels. Several times less computation for nearly
the same result. It's the basis of models that run on edge devices.

#### Q13.14 — How does a CNN handle different input image sizes?
Usually it doesn't — you resize or pad everything to one size first. If the
network ends with global pooling rather than a fixed dense layer, it can
tolerate some variation.

#### Q13.15 — What is a feature map?
The output of one filter applied across the whole image — a map showing where
that pattern was found.

#### Q13.16 — What are Vision Transformers, and when would you use one?
They chop the image into patches and let every patch look at every other patch,
instead of sliding a window.

They beat CNNs when you have enormous amounts of data. With limited data, and
for real-time detection, CNNs are still the right choice — which is the honest
answer for your projects.

## YOLO

#### Q14.1 — Classification vs detection vs segmentation?
Classification labels the whole picture: "there is a helmet in this image".
Detection adds boxes: "there is a helmet, **here**". Segmentation labels every
single pixel, so you get the exact outline.

#### Q14.2 — Why detection rather than classification for SafeSight?
Because the question is about individual workers, not the image. You need to
know **which** person is missing **which** item, and where they are, to produce
evidence a supervisor can act on.

#### Q14.3 — What does YOLO stand for, and what's the core idea?
"You Only Look Once." Older detectors first proposed regions that might
contain something, then classified each one — two passes. YOLO does the whole
thing in one pass over the image, which is what makes it fast enough for live
video.

#### Q14.4 — One-stage vs two-stage detectors?
Two-stage proposes candidate regions then examines each — historically more
accurate, much slower. One-stage predicts everything directly in a single
pass — fast enough for video, which is why you used it.

#### Q14.5 — Why YOLO rather than Faster R-CNN for CCTV?
Throughput. You have multiple camera streams running continuously; the
two-stage model couldn't keep up. And modern YOLO has closed most of the
accuracy gap anyway.

#### Q14.6 — What are anchor boxes?
A set of preset box shapes at each position. The model doesn't predict a box
from nothing — it predicts how to adjust the nearest preset shape, which is an
easier job.

#### Q14.7 — What is anchor-free detection, and which of your models uses it?
Predicting the box centre and size directly, with no preset shapes to adjust.

YOLOv8 is anchor-free; YOLOv5 is anchor-based. That's a genuine difference
between your two projects and a likely question.

#### Q14.8 — Main differences between YOLOv5 and YOLOv8?
v8 drops anchor boxes, splits the classification and box-position jobs into
separate heads instead of one shared head, removes the separate "is there
anything here" score, and ships with segmentation and pose as well as
detection.

Both are from Ultralytics and feel the same to use, which is why it's easy to
mistake it for a version bump.

#### Q14.9 — What do the n/s/m/l/x suffixes mean?
Model size — how wide and deep it is. Bigger means more accurate and slower.
You used the medium one.

#### Q14.10 — What is non-maximum suppression?
After detection you usually have several overlapping boxes on the same object.
NMS keeps the most confident one and deletes anything overlapping it heavily,
then repeats.

#### Q14.11 — What if the NMS threshold is too high or too low?
Too high and you keep several boxes on one person. Too low and you merge two
people standing close together into one detection — which is a real risk on a
busy work site.

#### Q14.12 — What is the confidence threshold, and how did you choose yours?
The minimum score before you report a detection. Lower it to catch more and
accept false alarms; raise it to be more certain and miss more.

For a safety system you lean towards catching more, because a missed violation
is worse than a supervisor glancing at a wrong one. For fire, even more so.

#### Q14.13 — What is YOLO's loss made of?
Three parts: how far off the box position was, whether the class was right,
and — in v5 — whether there was anything there at all. v8 drops that third part.

#### Q14.14 — What is mosaic augmentation?
Stitching four training images into one, so each training example contains
more objects, at more sizes, in more contexts. Ultralytics turns it on by
default and turns it off for the last few epochs.

#### Q14.15 — What is letterboxing, and why not just resize?
Scaling the image to fit and padding the leftover space with grey, instead of
stretching it.

A plain resize squashes people into the wrong proportions, which makes them
harder to detect.

#### Q14.16 — How do you label data for detection? What format does YOLO want?
Draw a box round each object in a tool like Roboflow, LabelImg or CVAT.

YOLO wants one text file per image, one line per object:
class, centre-x, centre-y, width, height — all as fractions of the image size.

#### Q14.17 — What is in a `data.yaml`?
Where the train, validation and test images are, how many classes there are,
and their names. Your fire config is one class, named "fire". Know that.

#### Q14.18 — How do you split video data for training? What's the trap?
**Split by clip or by camera — never by random frame.**

This is the important one. Frames half a second apart are almost identical. If
you split randomly, nearly identical pictures end up in both training and
validation, so the model is being tested on things it has effectively already
seen. Your score comes out far too high and you find out in production.

A sharp interviewer will ask this specifically.

#### Q14.19 — Your 5 PPE classes are imbalanced. How do you handle that?
Collect more pictures of the rare items. Oversample the images that contain
them. Use copy-paste augmentation to put more of them into scenes. Raise the
input resolution so small items are bigger.

And report the score per class rather than hiding behind the average.

#### Q14.20 — How do you detect small objects better?
Higher input resolution. Run detection on tiles of the image rather than the
whole thing shrunk down. Use the earlier, higher-resolution layers of the
network. Match the preset box sizes to the actual object sizes.

#### Q14.21 — What is an FPN or PANet?
A way of combining the network's detailed early layers with its
meaning-rich deep layers, so the detector works on both small and large
objects. YOLO's middle section does this.

#### Q14.22 — How do you link a PPE violation to a specific worker?
Detect people and detect safety items separately, then work out which item
belongs to which person — usually by checking whether the item's box sits
inside or overlaps the person's box. Then track people across frames so the
identity stays stable.

This is the real engineering problem in SafeSight. Be ready to say exactly
which approach you used and where it still fails — overlapping workers is the
honest weak point.

#### Q14.23 — What is object tracking, and name a tracker?
Keeping the same identity on the same person as they move between frames, so
one worker isn't counted as a new person every frame. SORT, DeepSORT,
ByteTrack, BoT-SORT.

#### Q14.24 — What's the difference between detection and tracking in your event log?
Enormous. Without tracking, a worker standing without a helmet for thirty
seconds generates hundreds of separate events. With tracking, that becomes
**one** violation with a duration.

That's the difference between a usable audit trail and noise.

#### Q14.25 — What is FPS, and what determines it in your pipeline?
Frames processed per second. Determined by model size, input resolution,
whether you're on a GPU, video decoding cost, and the NMS step.

You can also just skip frames. PPE compliance doesn't need thirty frames a
second — five is plenty, and that multiplies how many cameras you can handle.

#### Q14.26 — How do you deploy a detector on edge hardware?
Export it to a faster runtime, reduce the number precision, pick a smaller
model variant, and lower the resolution. Jetson devices if you need a GPU at
the edge.

#### Q14.27 — What is ONNX?
A common file format for models, so one trained in PyTorch can run in a
different, faster runtime without rewriting it.

#### Q14.28 — What is quantisation? What does it cost?
Storing the model's numbers at lower precision — 8-bit instead of 32-bit.
Smaller and faster, usually with only a small accuracy loss.

But measure it, don't assume it. On small objects the loss can be bigger than
you expect.

#### Q14.29 — What is model pruning?
Removing the weights or channels that barely contribute, making the model
smaller. Usually followed by a bit more training to recover what you lost.

#### Q14.30 — What is knowledge distillation?
Training a small model to copy a large model's outputs. You keep most of the
accuracy at a fraction of the cost.

#### Q14.31 — How would you handle night footage or a dirty lens?
Mainly by training on it — include low-light and degraded footage in the
dataset. Beyond that: infrared cameras, contrast enhancement, and monitoring
for when a camera's picture quality shifts so you know it needs cleaning.

#### Q14.32 — How do you know your deployed detector still works next month?
You don't have labels in production, so you watch for changes instead. Track
how many detections each camera produces and how confident they are. A sudden
drop on one camera means something changed — the lighting, the lens, or the
scene.

Then sample some frames for a human to check.

## OpenCV

#### Q15.1 — What is OpenCV?
A library for the practical side of working with images and video — reading
files, grabbing webcam frames, resizing, cropping, drawing boxes, writing
video out.

#### Q15.2 — How do you read and display an image?
`cv2.imread(path)`, then `cv2.imshow` and `cv2.waitKey(0)`.

#### Q15.3 — What's the gotcha with OpenCV colour channels?
OpenCV reads images as Blue-Green-Red. Almost everything else uses
Red-Green-Blue.

Forget to convert, and your model sees an image with the red and blue swapped.
It still runs — it just quietly performs worse. Very common bug.

#### Q15.4 — How do you capture webcam frames?
Open the camera, then loop reading one frame at a time, and release it at the
end. Your fire detector does exactly this.

#### Q15.5 — Why does your inference loop stutter if you send email inline?
Because sending an email takes a couple of seconds, and during that time
nothing is reading frames. The camera buffer fills up and you start dropping
frames or processing old ones.

Moving the email to a separate thread is why your fire detector stays
real-time. This is your best story in this section — it's specific, you
diagnosed it, and the fix is clean.

#### Q15.6 — How do you resize and crop?
`cv2.resize(img, (w, h))` to resize. To crop, just slice the array:
`img[y1:y2, x1:x2]`.

#### Q15.7 — How do you convert to greyscale, and why bother?
`cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`. It's a third of the data, and plenty
of classical operations only care about brightness, not colour.

#### Q15.8 — What is Gaussian blur for?
Smoothing out noise before you look for edges or apply a threshold. Without
it, every speck of noise looks like an edge.

#### Q15.9 — What is thresholding? What is Otsu's method?
Turning a greyscale image into pure black and white at some cutoff. Otsu's
method picks that cutoff for you automatically based on the image.

#### Q15.10 — What is Canny edge detection?
A multi-step edge finder: blur, find where brightness changes sharply, thin
those down to single lines, then keep the strong ones and any weak ones
connected to them.

#### Q15.11 — What are morphological operations?
Simple shape operations on black-and-white images. Erosion shrinks the white
regions, dilation grows them. Combining them removes small specks or fills
small holes. Used to tidy up masks.

#### Q15.12 — What is contour detection used for?
Finding the outlines of connected shapes in a black-and-white image, so you can
get each one's area, centre or bounding box.

#### Q15.13 — How do you draw boxes and labels on a frame?
`cv2.rectangle` and `cv2.putText`. That's how your evidence images get their
annotations.

#### Q15.14 — How do you write an output video?
Create a `VideoWriter` with the output path, codec, frame rate and frame size,
then write each frame to it.

#### Q15.15 — Classical CV vs deep learning — is OpenCV obsolete?
No. Deep models do the recognition; OpenCV does everything around them —
reading the video, resizing, colour conversion, drawing the output, saving the
result. Every one of your vision projects uses both.

:::practice The two that decide this round
Q14.18 — splitting video by clip rather than frame. And Q14.22 — how you link
a violation to a specific worker. Those two separate someone who ran a YOLO
tutorial from someone who built a system.
:::

:::recap
- A convolution slides one detector across the whole image, which is why it
  needs far fewer weights than a dense layer.
- YOLO does detection in one pass, which is what makes live video possible.
- v8 is anchor-free, v5 is anchor-based — know this, it's your two projects.
- Split video by clip, never by random frame. This is the question that
  catches people.
- Tracking turns hundreds of frame events into one violation with a duration.
- OpenCV reads images as BGR, not RGB.
- The threaded email fix is your best concrete engineering story.
:::

# ``mriseqplot``

``mriseqplot`` is a python module to generate and render MRI sequence diagrams with.
It's early days for the project and its main mission now is to provide a simple API
to generate neat tweakable sequence diagrams.

## Logic

In a nutshell, ``mriseqplot`` allows you to map a sequence of events to a figure
with a desired number of axes.

``Sequence`` class represents an MRI sequence as a combination of  logical channels,
or sequence of events, played out by the scanner.
For example, a sequence of RF pulses might be combined together into one "channel",
while a sequence of readout gradients can be combined into another "channel".
Every channel is represented as a single ``numpy`` array with 1 or 2 dimensions,
with one axis representing time, and another potentially allowing to stack multiple
events on top of each other (e.g. to represent all phase encoding gradients at once).

Next, the sequence of these channels must be mapped onto a figure. By default, each
logical channel represented by ``Sequence`` receives its own axis, however
``mriseqplot`` allows to map a number of channels to one (e.g. to represent RF and ADC
on one axis).


## Installing ``mriseqplot``

``mriseqplot`` is not yet on PyPI, neither it is available through anaconda. To install the module, clone the repository from GitHub

```sh
git clone git@github.com:Sibgatulin/mriseqplot.git
```

and then install via ``pip``

```sh
pip install mriseqplot
```

or if you plan to modify the code, install it in «editable» mode

```sh
pip install -e mriseqplot
```
Furthermore, if you intend to commit to the repository, you'll need ``pre-commit``, so
we recommend you go with the dev ``extra`` requirements (mind no space before ``[``)
and set ``pre-commit`` up:

```sh
pip install -e mriseqplot[dev]
pre-commit install
```

## Contributing to ``mriseqplot``

The project tries to stick with PEP8 and encourages to use ``black`` (see installation
above).
Occasionally, there are some [type hints](https://www.python.org/dev/peps/pep-0484)
but their use is so far... Experimental? 🤔🤷

## License

``mriseqplot`` is licensed under the terms of the MIT license.
Please see the [LICENSE file](https://github.com/Sibgatulin/mriseqplot/blob/master/LICENSE).

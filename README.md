# YACRAF-calculator

This is a graphical tool for doing calculations according to YACRAF (https://link.springer.com/article/10.1007/s10207-023-00713-y) used in the KTH courses EP2790 and EP279V.

This tool allows calculations inherent to the threat modeling to be set up and calculated using graphical block diagrams, where one can place, drag, and connect different blocks across various `Views`. The aim of the tool is to allow for the: (i) automation of the calculation process, where any changes to any block automatically propagate through the system, and (ii) simulation of various scenarios.

## Dependecies

The program utilizes Tkinter for its GUI and NumPy for its calculations. If not already installed, Tkinter can on Debian-based Linux distributions (such as Ubuntu) be installed using:

```
sudo apt install python3-tk
```

Meanwhile, NumPy can be installed using:

```
pip install numpy
```

Make sure Python is not outdated. Required is at least Python 3.7, where 3.10 was used during the development of the program.

## How to use

Run the program using:

```
python3 main.py
```

The graphical interface consists of two types of `Views`: `Configuration Views` and `Setup Views`. `Class` blocks (for example, an attack event) and their `Attributes` (for example, the attack event's cost) are defined within `Configuration Views`, where one may also define connections or relationships between different `Attributes`. For instance, whether a specific `Attribute` takes other ones as input and what operation to perform between them. In practical terms, `Configuration Views` defines the metamodel used during the threat modeling. Meanwhile, `Setup Views` define the system-specific setup using the configured `Class` and how they connect/relate to each other.

### Views

In the top right corner of the GUI are two columns of buttons, see (1) and (2) in the below figure. The figure shows a `Configuration View`. These buttons switch between the different `Views` where the left-most column switches between `Configuration Views` and the right-most between `Setup Views`. The button with the `+` allows for an additional `View` to be added. The current `View` can be configured by pressing E (for edit) when no block inside the `View` is selected (will edit the block otherwise), where one can:

1. Change its name
2. Switch their button order
3. Delete it

The `Save` button in the bottom left corner ((3) in the below figure) saves the current state of all `Configuration Views` and `Setup Views`. Any blocks in the `Views` can be deleted by pressing backspace when selected.

![Image of a configuration view for the Yacraf metamodel](img/configuration_view.svg)

### Configuration View

#### Class

A new metamodel `Class` is created by pressing the `Add class` button in the top left corner, as illustrated by (1) in the below figure. By pressig the (2), one can add an `Attriubte` to the created `Class` (result shown in (3)). Pressing an `Attribute` selects it, as shown by (4), where one can edit it by pressing E. Editing an `Attribute` allows the following to be configured:

1. Its name
2. Their displayed order
3. The value type of the `Attribute`, such as a single number or a triangle distribution
4. Hide it from the corresponding `Setup Views`, meaning it is only visible in the `Configuration Views` (useful for calculations requiring several steps)

Similarly, the `Class` itself can be also be edited, enabling:

1. Changing its name
2. Creating a linked copy of this instance to another `Configuration View` (allowing relations between blocks across `Configuration Views`), identified by a marker in their upper right corner

![Image of a configuration view where one adds classes and attributes, and subsequently connects them](img/configuration.svg)

#### Calculation input

By pressing the `Add input` in the top left corner (see (5) in the above figure), an `Input` block is created (see (6)). `Input` blocks function take inputs from one or more `Attributes` and, through a specified mathematical operation, outputs the result to an adjacent `Attribute` that it has been dragged next to (see (7)). The `Input` block can be configured by selecting it and pressing E (see (8)), where one can:

1. Change its mathematical operation, for example AND, OR, multiplication, etc
2. Add a scalar that multiplies the calculated input with a factor (see (10))

`Attributes` can be added as inputs (connecting them) to the `Input` block by first right clicking on the corresponding `Attribute` and then left or right clicking the `Input` block, creating a `Connection` between the two, as shown by (9) in the above figure.

##### Connection

Pressing E when the corner of a `Connection` is selected opens up its configuration, where one can:

1. Set the `Connection` as external, meaning it will only be connected to `Attributes` of other class instances, ignoring connected internal `Attributes`, such as an attack event only considering the input of another attack event and not that of itself `Attribute` (indicated by its lines becoming dashed)

The corners can be dragged around to customize the path of the `Connection`.

### Setup View

Shown in the below figure is an example of a `Setup View` representing the system which the metamodel from the `Configuration Views` has been applied to. The buttons at (1) in the below figure are used to create `Connections` between the `Classes` and calculate the final values, respectively. (2) shows buttons for running custom scripts that can calculate/simulate different scenarious throughout the `Setup Views`. Scripts are explained later.

![Image of a setup view](img/setup_view.svg)

#### Class

An instance of a `Class` from a `Configuration View` can be added to the current `Setup View` by pressing the corresponding button in the top left corner, as shown by (1) in the `Setup View` in the below figure. The `Class` instances can be configured by pressing E when selected, where one can:

1. Change the name of the corresponding `Class` instance
2. Create a linked copy of the instance to another `Setup View` (any calculated value takes all linked versions into account), identified by a marker in their upper right corner

![Image of a setup view where classes from the configuration views are added and subsequently connected](img/setup.svg)

#### Connection

Pressing the `Connection` button at the top ((3) in the above figure) creates a directional `Connection` that can be attached to `Classes` by dragging its corresponding ends. The `Attributes` of the `Class` that the `Connection` points to may take input from the other `Class`, if such a relation has been configured in the `Configuration Views`. Attaching a `Connecton` to a `Class` will automatically disable `Attribute` entries if the corresponding value is dependent on at least one connected `Class`. By pressing E after selecting a corner on the directional `Connection`, one can configure it by:

1. Adding scalar(s) that is applied to input values from the `Connection`, where the appearing indicator (see (6)) can be dragged along the path of the `Connection`

##### Calculate

The calculate button at the top (see (7)) calculates the values of all `Attributes` that do not have an input entry field. Calculated are the `Attributes` of all `Classes` in all `Setup Views`. In the case of the above figure, the `Attribute` indicated by (8) has been calculated using the corresponding `Attribute` values of its input `Classes`. The input `Attributes` in question are highlighted when selecting an `Attribute`.

#### Scripts

Scripts to visualize or simulate different scenarios, such as finding the most optimal order of implementing defense mechanisms, or enumerating and visualising the several of the easiest attack paths, can be created using Python scripts that interface to the tool. To create a script, go to the `scripts` directory.


# YACRAF-calculator

This is a graphical tool for doing calculations according to YACRAF (https://link.springer.com/article/10.1007/s10207-023-00713-y) used in the KTH courses EP2790 and EP279V.

This tool allows calculations inherent to the threat modeling to be setup and calculated using graphical block diagrams, where one can place, drag, and connect different blocks across various `Views`. The aim of the tool is to allow for the: (i) automation of the calculation process, where any changes to any block automatically propagate through the system, and (ii) simulation of various scenarios.

## Dependecies

The program utilizes the Tkinter for its GUI and NumPy for its calculations. If not already installed, Tkinter can on Debian-based Linux distributions (such as Ubuntu) be installed using:

```
sudo apt install python3-tk
```

Meanwhile, NumPy can be installed using:

```
pip install numpy
```

## How to use

Run the program using:

```
python3 main.py
```

The graphical interface consists of two types of `Views`: `Configuration Views` and `Setup Views`. `Class` blocks (for example, attack event) and their `Attributes` (for example, cost) are defined within `Configuration Views`, where one may also define connections or relationships between different `Attributes`: whether a specific `Attribute` takes other ones as input and what operation to perform between them. In practical terms, `Configuration Views` defines the metamodel used during the threat modeling. Meanwhile, `Setup Views` define the system-specific setup. That is, what instances of defined `Class` blocks exist within the analysed system, but also its system-specific connections.

### Views

In the top right corner of the GUI are two columns of buttons, see (1) and (2) in the below figure showing a `Configuration View`. These buttons switch between the different `Views` where the left-most column switches between `Configuration Views` and the right-most between `Setup Views`. The button with the `+` allows for an additional `View` to be added. The current `View` can be configured by pressing E (for edit) when no block is selected (will edit the block otherwise), where one can:

1. Change its name
2. Switch their displayed order
3. Delete it

The `Save` button in the bottom left corner, (3) in the below figure saves the current state of all `Configuration Views` and `Setup Views`. Any blocks in the views can be deleted by pressing backspace.

![Image of a configuration view for the Yacraf metamodel](img/configuration_view.svg)

### Configuration View

#### Class

A new metamodel `Class` is created by pressing the `Add class` button in the top left corner, as illustrated by (1) in the below figure. By pressig the (2), one can add an `Attriubte` to the created `Class` (result showin in (3)). Pressing an `Attriubte` selects, ashown by (4), where one can edit it by pressing E, where on can:

1. Change its name
2. Change the displayed order of the `Attributes`
3. Change the type of value of the `Attribute`, such as a decimal number or a triangle distribution
4. Hide it from the corresponding `Setup Views`, meaning it is only visible in the `Configuration Views`

Similarly, the `Class` itself can be also be edited, allowing for:

1. Changing its name
2. Creating a linked copy of this instance to another `Configuration View` (allowing relations between blocks across `Configuration Views`), identified by the marker in their upper right corner

![Image of a configuration view where one adds classes and attributes, and subsequently connects them](img/configuration.svg)

#### Calculation input

By pressing the `Add input` in the top left corner (see (5) in the above figure), an `Input` block is created (see (6)). `Input` blocks function take inputs from one or more `Attributes` and, through a specified mathematical operation, outputs the result to an adjacent `Attribute` that it has been dragged next to (see (7)). The `Input` block can be configured by selecting it and pressing E (see (8)), where one can:

1. Change its mathematical operation, for example AND, OR, multiplication, etc
2. Add a scalar that multiplies the calculated input with a factor (see (10))

`Attributes` can be added as inputs (connecting them) to the `Input` block by first right clicking on the corresponding `Attribute` and then left or right clicking the `Input` block, creating a `Connection` between the two, as shown by (9) in the above figure.

##### Connection

Pressing E when a corner on a `Connection` is selected opens up its configuration, where one can:

1. Set the `Connection` as external, meaning it will only be connected to `Attributes` of other instances of its `Class` type, such as an attack event only considering the input of another attack event and not an internal `Attribute` (indicated by its lines becoming dashed)

The corners can be dragged around to customize the path of the `Connection`.

### Setup View

Shown in the below figure is an example of a `Setup View` representing the system which the metamodel from the `Configuration Views` has been applied to. The buttons at (1) in the below figure are used to create `Connections` between the `Classes` and calculate the corresponding values, respectively. (2) shows buttons for running custom scripts that can calculate/simulate different scenarious throughout the `Setup Views`. More on the scripts later.

![Image of a setup view](img/setup_view.svg)

#### Class

An instance of a `Class` from a `Configuration View` can be added to the current `Setup View` by pressing the corresponding button in the top left corner, as shown by (1) in the `Setup View` in the below figure. The `Class` instances can be configured by pressing E when selected, where one can:

1. Change the name of the corresponding `Class` instance
2. Create a linked copy of the instance to another `Setup View` (any calculated value takes all linked versions into account), identified by a marker in its upper right corner

![Image of a setup view where classes from the configuration views are added and subsequently connected](img/setup.svg)

#### Connection

Pressing the `Connection` button at the top ((3) in the above figure) creates a directional `Connection` that can be attached to `Classes` by dragging its corresponding ends. The `Attributes` of the `Class` that the `Connection` points to may take input from the other `Class`, if such a relation has been configured in the `Configuration Views`. Attaching a `Connecton` to a `Class` will automatically disable `Attribute` entries if the corresponding value is dependent on at least one connected `Class`. By pressing E when a corner on the directional `Connection` is selected opens its configuration, where one can:

1. Add scalar(s) that is applied to input values from the `Connection`, where the appearing indicator (see (6)) can be dragged along the path of the `Connection`

##### Calculate

The calculate button at the top (see (7)) calculates the values of all `Attributes` that do not have an input entry field. Calculated are the `Attributes` of all `Classes` in all `Setup Views`. In the case of the above figure, the `Attribute` indicated by (8) has been calculated using the corresponding `Attribute` values of its input `Classes`. The input `Attributes` in question are highlighted when selecting an `Attribute`, as shown by (8).

#### Scripts

Scripts to visualize or simulate different scenarios, such as finding the most optimal order of implementing defense mechanisms, or enumerating and visualising the easiest attack paths, can be created using Python scripts that interface to the tool. To create a script, go to the `scripts` directory.

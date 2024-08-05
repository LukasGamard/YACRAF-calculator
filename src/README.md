# Code structure

Found in the `blocks_calculation` directory are the `Class` and `Attribute` classes used to track relations between blocks and calculate any values. Meanwhile, the `blocks_gui` directory contain the corresponding GUI versions, wrapping the original ones.

The `Model` class tracks and manages the main objects of the program, where the `View` class tracks any `View` specific objects and draws corrsponding GUI. When editing a block, the window that pops up is the `Options` class.

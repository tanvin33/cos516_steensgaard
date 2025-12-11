# cos516_steensgaard
Final project for COS 516, Implementing Steensgaard’s pointer analysis

Authors: Tanvi Namjoshi & Lana Glisic


### Usage
To run this code first make sure you have installed all the required packages in listed in `requirements.txt`. 

To run Steensgaard's analysis on the a program `test.sil` run the following command 
```shell
python3 steensgaard.py -fn "test.sil"
```

This should open visualization of the storage shape graph, as well as save it to the png   `test.sil_graph.png`. The code will also output a final typing to the terminal.

The reference language for writing a sil program can be foundin `sil_ref.txt`. It is parsed using `sil_parser.py`.

### Testing
There are a bunch of example test programs in the `tests/` directory, as well as their corresponding graphs. There are also some programs we wrote to test the correctness of the parser, found in `parser_tests/`. To test the parser you can run `python sil_parser.py -fn <filename>`. 

We also wrote some test cases to verify the correctness of the Union-Find datastructure in `union_find_test.py`.
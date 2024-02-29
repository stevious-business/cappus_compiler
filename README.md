# CFC
 Compiler for the CAPPUS processor

## Stages

### 0. Preprocessor / "Source"
TODO: Implement proper preprocessing step with macro substitution etc.

In the first compilation step, CPL code is loaded using a "source" class.
The source class loads a file that is passed as a file object (as obtained e.g. via `open()`), and maintains a pointer pointing to a certain character in the file.
The advantage of using a `Source` object, as opposed to reading bytes from the file immediately, is that it _preprocesses_ the file, i. e. skipping comments. This makes it very easy to use with further processing steps such as lexers.
The source class interface is as follows:

- **Initialization**: <br>
A source object can be initialised as follows:
`Source(file: <File object>)` <br>
The initialisation will automatically fetch necessary data from the file.
- **Getting characters**: <br>
The `get()` method returns the next character in the file, i. e. the character that is pointed to by the class's internal pointer, which is incremented by this method. If the next character is the first character of a comment, the comment is skipped, the first character after the comment is returned, and pointers are adjusted accordingly.
- **Peeking characters**: <br>
The `peek(depth=1)` method behaves similarly to the `get()` method, the most notable difference being that `get()` also increments the object's internal pointer.
Additionally, the `peek()` method offers for use with the keyword argument _depth_, which will obtain a character at position _internalPointer+depth_ in the file. _depth_ defaults to 1.
- **Obtaining file position / stamp**: <br>
The `get_pos()` method returns a string in the format: `<filename> <line>:<column>`, which is useful for debugging and producing helpful errors.

### Lexer
Is very _baller_.

### Parser
makes ast idk

### Code generator
forgor to implement front and middle end :skull:
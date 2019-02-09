# Py2TeX: The Python to LaTeX converter

Did you ever feel overwhelmed by the cumbersomeness of LaTeX to produce quality tables and figures? Fear no more, Py2TeX is here! Produce perfect tables automatically and easily, create figures and plots that integrates seamlessly into your tex file, or even write your complete article directly from Python! All that effortlessly (or almost) with Py2TeX. (Plots and figures to come)

## Examples

### Create a simple document

The following example shows how to create a document with a single section and some text.
```python
from py2tex import Document

doc = Document(filename='Test', doc_type='article', options=('12pt',))
doc.set_margins(top='3cm', bottom='3cm', margins='2cm')
sec = doc.new_section('Spam and Egg', label='spam_egg')
sec.add_text('The mighty Python slays the Spam and eats the Egg.')

tex = doc.build() # Builds to tex and compile to pdf
print(tex) # Prints the tex string that generated the pdf
```

### Create a table from a numpy array

This example shows how to generate automatically a table from data taken directly from a numpy array. The module allows to add merged cells easily, to add rules where you want and even to highlight the best value automatically inside a specified area! To ease these operations, the the square brackets ('getitem') operator have been repurposed to select an area of the table instead of returning the actual values contained in the table. Once an area is selected, use the 'multicell', 'add_rule' or 'highlight_best' methods. To get the actual values inside the table, one can use the 'data' attribute of the table.
```python
from py2tex import Document, Table
import numpy as np

doc = Document(filename='Test', doc_type='article', options=('12pt',))

sec = doc.new_section('Testing tables')
sec.add_text("This section tests tables.")

col, row = 4, 4
data = np.random.rand(row, col)

table = sec.new(Table(shape=(row+1, col+1), alignment='c', float_format='.2f'))
table.caption = 'test' # Set a caption if desired
table[1:,1:] = data # Set entries with a slice directly from a numpy array!

table[2:4,2:4] = 'test' # Set multicell areas with a slice too. The value is contained in the top left cell (here it would be cell (2,2))
table[0,1:].multicell('Title', h_align='c') # Set a multicell with custom parameters
table[1:,0].multicell('Types', v_align='*', v_shift='-2pt')

table[0,1:3].add_rule(trim_left=True, trim_right='.3em') # Add rules with parameters where you want
table[0,3:].add_rule(trim_left='.3em', trim_right=True)

table[1,1:].highlight_best('low', 'bold') # Automatically highlight the best value inside the specified slice
table[4,1:].highlight_best('low', 'bold')

tex = doc.build()
print(tex)
```

### Create an unsupported environment
```python
from py2tex import Document, TexEnvironment

doc = Document(filename='Test', doc_type='article', options=('12pt',))

sec = doc.new_section('Unsupported env')
sec.add_text("This section shows how to create unsupported env if needed.")

spam = sec.new(TexEnvironment('spam', 'options', label='spam_label'))
spam.add_text('Inside spam env!')

tex = doc.build(compile_to_pdf=False)
print(tex)
```

## How it works

This LaTeX wrapper is based on the TexEnvironment class. Each such environment possesses a body attribute consisting in a list of strings and of other TexEnvironments. The 'build' method then converts every TexEnvironment to a tex string recursively. This step makes sure every environment is properly between a '\begin{env}' and a '\end{env}'. Converting the document to a string only at the end allows to do operation in the order desired, hence providing flexibility. The 'build' method can be called on any TexEnvironment, return the tex string representation of the environment. However, only the Document class 'build' method will also compile it to an actual pdf.
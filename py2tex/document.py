import os
from subprocess import DEVNULL, STDOUT, check_call

import numpy as np


class TexFile:
    """
    Class that compiles python to tex code. Manages write/read tex.
    """
    def __init__(self, filename):
        self.filename = filename + '.tex'

    def save(self, tex):
        with open(self.filename, 'w', encoding='utf8') as file:
            file.write(tex)

    def compile_to_pdf(self):
        check_call(['pdflatex', self.filename], stdout=DEVNULL, stderr=STDOUT)


class TexEnvironment:
    def __init__(self, env_name, *parameters, options=None, parent_doc=None):
        self.env_name = env_name
        self.body = [] # List of Environments or texts
        self.head = '\\begin{{{env_name}}}'.format(env_name=env_name)
        self.tail = '\\end{{{env_name}}}'.format(env_name=env_name)
        if parameters:
            self.head += f"{{{','.join(parameters)}}}"
        if options:
            self.head += f"[{options}]"
        self.parent_doc = parent_doc

    def add_text(self, text):
        self.body.append(text)

    def new_environment(self, env_name, *parameters, options=None):
        env = TexEnvironment(env_name, *parameters, options=None, parent_doc=self.parent_doc)
        self.body.append(env)
        return env

    def new_table(self, *parameters, position='h!', **options):
        table = Table(*parameters, position, parent_doc=self.parent_doc, **options)
        self.body.append(table)
        return table

    def __repr__(self):
        return f'TexEnvironment {self.env_name}'

    def build(self):
        for i in range(len(self.body)):
            line = self.body[i]
            if isinstance(line, TexEnvironment):
                line.build()
                self.body[i] = line.body
        first_line = f'\\begin{{{self.env_name}}}'

        self.body = [self.head] + self.body + [self.tail]
        self.body = '\n'.join(self.body)


class Document(TexEnvironment):
    """
    Tex document class.
    """
    def __init__(self, filename, doc_type, *options, **kwoptions):
        super().__init__('document')
        self.head = '\\begin{document}'
        self.tail = '\\end{document}'
        self.filename = filename
        self.file = TexFile(filename)
        self.parent_doc = self

        options = list(options)
        for key, value in kwoptions.items():
            options.append(f"{key}={value}")
        options = '[' + ','.join(options) + ']'

        self.header = [f"\documentclass{options}{{{doc_type}}}"]

        self.packages = {'inputenc':'utf8',
                         'geometry':''}
        self.set_margins('2.5cm')

    def __repr__(self):
        return f'Document {self.filename}'

    def add_package(self, package, *options, **kwoptions):
        options = f"[{','.join(options)}]" if options else ''
        if kwoptions:
            for key, value in kwoptions.items():
                options.append(f"{key}={value}")
        self.packages[package] = options

    def set_margins(self, margins, top=None, bottom=None):
        self.margins = {'top':margins,
                         'bottom':margins,
                         'margin':margins}
        if top is not None:
            self.margins['top'] = top
        if bottom is not None:
            self.margins['bottom'] = bottom

        self.packages['geometry'] = ','.join(key+'='+value for key, value in self.margins.items())

    def build(self):
        for package, options in self.packages.items():
            if options:
                options = '[' + options + ']'
            self.header.append(f"\\usepackage{options}{{{package}}}")
        self.header = '\n'.join(self.header)

        super().build()
        self.file.save(self.header + '\n' + self.body)
        self.file.compile_to_pdf()


class Table(TexEnvironment):
    """

    """
    def __init__(self, position='h!', shape=(1,1), **kwargs):
        """
        Args:

        """
        super().__init__('table', options=position, **kwargs)
        self.head += '\n\centering'
        self.tabular = Tabular(shape, **kwargs)
        self.body = [self.tabular]

    def __getitem__(self, i):
        return self.tabular[i]

    def __setitem__(self, i, value):
        self.tabular[i] = value

    def add_rule(self, *args, **kwargs):
        self.tabular.add_rule(*args, **kwargs)

    def build(self):
        super().build()


class Tabular(TexEnvironment):
    """
    Implements the 'tabular' environment from the package 'booktabs'.
    """
    def __init__(self, shape=(1,1), alignment='c', float_format='.2f', **kwargs):
        """
        Args:
            shape (tuple of 2 ints):
            alignment (str, either 'c', 'r', or 'l'):
            float_format (str): Standard Python float format available.
            kwargs: See TexEnvironment keyword arguments.
        """
        super().__init__('tabular', **kwargs)
        self.parent_doc.add_package('booktabs')

        self.shape = shape
        self.alignment = np.array([alignment], dtype=str)
        self.float_format = float_format
        self.data = np.empty(shape, dtype=object)
        self.rules = {}

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, value):
        self.data[i] = value

    def add_rule(self, row, col_start=None, col_end=None, trim_right=False, trim_left=False):
        """
        Args:
            row (int): Row number under which the rule will be placed.
            col_start, col_end (int or None): Columns from which the rule will stretch. Standard slicing indexing from Python is used (first index is 0, last is excluded, not the same as LaTeX). If both are None (default) and both trim are False, the rule will go all the way across and will be a standard "\midrule". Else, the "\cmidrule" command is used.
            trim_left (bool or str): Whether to trim the left end of the rule or not. If True, default trim length is used ('.5em'). If a string, can be any valid LaTeX distance.
            trim_right (bool or str): Same a trim_left, but for the right end.
        """
        r = 'r' if trim_right else ''
        if isinstance(trim_right, str):
            r += f"{{{trim_right}}}"
        l = 'l' if trim_left else ''
        if isinstance(trim_left, str):
            l += f"{{{trim_left}}}"
        self.rules[row] = (col_start, col_end, r+l)

    def build_rule(self, start, end, trim):
        if start is None and end is None and not trim:
            rule = "\midrule"
        else:
            rule = "\cmidrule"
            if trim:
                rule += f"({trim})"
            start, end, step = slice(start, end).indices(self.shape[1])
            rule += f"{{{start+1}-{end}}}"
        return rule

    def build(self):
        row, col = self.data.shape
        self.head += f"{{{'c'*col}}}\n\\toprule"
        self.tail = '\\bottomrule\n' + self.tail

        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if isinstance(value, float):
                    entry = f'{{value:{self.float_format}}}'.format(value=value)
                else:
                    entry = str(value)
                self.data[i,j] = entry

        for i, row in enumerate(self.data):
            self.body.append(' & '.join(row) + '\\\\')
            if i in self.rules:
                rule = self.build_rule(*self.rules[i])
                self.body.append(rule)
                print(rule)

        super().build()


if __name__ == "__main__":
    doc = Document('Test', 'article', '12pt')

    sec = doc.new_environment('section', 'Testing tables')
    sec.add_text("This section tests tables.")

    col = 4
    row = 4
    data = np.array([[np.random.rand() for i in range(j,j+col)] for j in range(1, col*row, col)])

    table = sec.new_table(shape=data.shape)
    table[:,:] = data
    table[0] = 'Title'
    table.add_rule(0)#, trim_left=True, trim_right='1em')
    # print(table.tabular.rules)

    doc.build()
    print(doc.body)

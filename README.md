# declPyQt5

A declarative UI library that works as an adapter for PyQt5.

Inspired by Flutter.

Currently only supports static routes.

```python
from declpyqt5 import *

def uiMainRoute(context: BuildContext) -> Widget:
    def onSelected(row, col, value):
        print('selected (%d, %d)' % (row, col))

    def onChanged(row, col, value):
        print('changed (%d, %d) to %s' % (row, col, value))

    return Row(
        children=[
            Expanded(
                child=Text('Sample text widget'),
                flex=2,
            ),
            Expanded(
                child=TableView(
                    rows=4,
                    columns=3,
                    headers=['Col 1', 'Col 2', 'Col 3'],
                    data=[[1, 2, 3], ['a', 'b', 'c'], [4, 5, 6], [7, 8, 9]],
                    onSelected=onSelected,
                    onChanged=onChanged,
                ),
                flex=8,
            ),
        ],
    )

if __name__ == '__main__':
    context = BuildContext(None)
    # create application
    app = Application(
        context=context,
        builder=uiMainRoute,
        title='Example declPyQt5 app',
        width=1024,
        height=768,
    )
    app.run()
```


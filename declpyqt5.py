
# declPyQt5, Copyright (C) 2021 jeffswt
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the “Software”), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import enum
import PyQt5.QtCore
import PyQt5.QtWidgets
from typing import List, Dict, Any, Union, Callable
import uuid


class BuildContext:
    """ This shares the state between widgets. """
    def __init__(self, application):
        self._application = application
        self.counter = 0

    def setState(self):
        if self._application:
            self._application.setState()
    pass


class Key:
    """ Basic key to distinguish widgets. There is only one basic key. You may
    use the == comparator to compare between different keys. """
    def __init__(self):
        return

    def __eq__(self, other) -> bool:
        return True
    pass


class ValueKey(Key):
    """ A key that is represented by its value. """
    def __init__(self, value: Any):
        self._value = value
        return

    def __eq__(self, other) -> bool:
        if not isinstance(other, ValueKey):
            return False
        return self._value == other._value
    pass


class UniqueKey(Key):
    """ All UniqueKeys are different. """
    def __init__(self):
        self._hash = uuid.uuid4()
        return

    def __eq__(self, other) -> bool:
        if not isinstance(other, UniqueKey):
            return False
        return self._hash == other._hash
    pass


class Widget:
    def __init__(self, key: Key = Key()):
        """ This is where the initial parameters are loaded. """
        self._key = key
        self._context = None
        self._hash = 0
        return

    def build(self, context: BuildContext) -> None:
        """ This will be called when the widget tree is expanded to a large
        and full widget tree. Nothing natively related should be done here.
        Also, you are expected to update your hash in this function, so as to
        determine the differentiation between different build()s. Note that you
        are not required to return anything, just build the tree. """
        self._context = context
        self._hash = 0
        return

    def paintWidget(self) -> Any:
        """ This will be called when the widget tree is (at the first time)
        converted into a Qt widget tree. You are expected to return a Qt
        widget from here for upper level functions to work. """
        return

    def setState(self) -> None:
        """ This calls the application to repaint the widget tree, updating
        widgets if necessary. """
        if self._context is None:
            print('attempted setState() on an unbuilt widget')
        self._context.repaint()
        return
    pass


class Text(Widget):
    """ Text label. """
    def __init__(self, text: str, key: Key = Key()):
        super(Text, self).__init__(key)
        if text is None:
            text = ''
        self._text = text
        return

    def build(self, context: BuildContext):
        super(Text, self).build(context)
        self._hash = hash('Text(text=%s)' % self._text)
        return

    def paintWidget(self) -> Any:
        self._widget = PyQt5.QtWidgets.QLabel(self._text)
        return self._widget
    pass


class LabelButton(Widget):
    """ Clickable labeled button. """
    def __init__(self, key: Key = Key(), label: str = '', tooltip: str = '',
                 onTap: Callable = None):
        super(LabelButton, self).__init__(key)
        self._label = label
        self._tooltip = tooltip
        self._ontap = onTap
        return

    def build(self, context: BuildContext):
        super(LabelButton, self).build(context)
        self._hash = hash('LabelButton(label=%s,tooltip=%s,onTap=%s)' % (
            self._label, self._tooltip, type(self._ontap)))
        return

    def paintWidget(self) -> Any:
        self._widget = PyQt5.QtWidgets.QPushButton(self._label)
        self._widget.setToolTip(self._tooltip)
        if self._ontap is not None:
            self._widget.clicked.connect(self._ontap)
        return self._widget
    pass


class TextField(Widget):
    """ Text field allowing entering text. """
    def __init__(self, key: Key = Key(), placeholder: str = '',
                 value: str = '', hidden: bool = False,
                 onChanged: Callable[[str], None] = None):
        super(TextField, self).__init__(key)
        self._placeholder = placeholder
        self._value = value
        self._onchanged = onChanged
        self._hidden = hidden
        return

    def build(self, context: BuildContext):
        super(TextField, self).build(context)
        self._hash = hash(
            'TextField(placeholder=%s,hidden=%s,onChanged=%s)' %
            (self._placeholder, self._hidden, type(self._onchanged)))
        return

    def paintWidget(self) -> Any:
        self._widget = PyQt5.QtWidgets.QLineEdit()
        self._widget.setText(self._value)
        if self._hidden:
            self._widget.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self._widget.textChanged.connect(self._onchanged)
        return self._widget
    pass


class Expanded(Widget):
    """ Expandeds widget to flex in order to fit it inside AxisAlignedBox. """
    def __init__(self, key: Key = Key(), child: Widget = None, flex: int = 1):
        super(Expanded, self).__init__(key)
        if child is None:
            raise ValueError('Expanded must have a non-null child')
        if not isinstance(flex, int) or flex <= 0:
            raise ValueError('flex must be a non-negative integer')
        self._child = child
        self._flex = flex
        return

    def build(self, context: BuildContext):
        super(Expanded, self).build(context)
        self._child.build(context)
        self._hash = hash('Expanded(child=%s,flex=%d)' % (
            self._child._hash, self._flex))
        return

    def paintWidget(self) -> Any:
        self._widget = self._child.paintWidget()
        return self._widget
    pass


class Alignment(enum.Enum):
    none = 0
    start = 1
    center = 2
    end = 3


class AxisAlignedBox(Widget):
    """ Vertical or horizontal alignment. """
    def __init__(self, key: Key = Key(), children: List[Widget] = [],
                 vertical: bool = True, alignment: Alignment = Alignment.none):
        super(AxisAlignedBox, self).__init__(key)
        self._children = []
        # stat expanded
        has_expanded = False
        for child in children:
            if child is not None:
                if isinstance(child, Expanded):
                    has_expanded = True
        # fake alignment
        if not has_expanded:
            if alignment in {Alignment.center, Alignment.end}:
                self._children.append(Expanded(child=Text(''), flex=1))
        # add children
        for child in children:
            if child is not None:
                self._children.append(child)
        # fake alignment
        if not has_expanded:
            if alignment in {Alignment.start, Alignment.center}:
                self._children.append(Expanded(child=Text(''), flex=1))
        self._vertical = vertical
        return

    def build(self, context: BuildContext):
        super(AxisAlignedBox, self).build(context)
        for child in self._children:
            child.build(context)
        self._hash = hash('AxisAlignedBox(children=[%s])' % ','.join(map(
            lambda child: str(child._hash), self._children)))
        return

    def paintWidget(self) -> Any:
        if self._vertical:
            self._layout = PyQt5.QtWidgets.QVBoxLayout()
        else:
            self._layout = PyQt5.QtWidgets.QHBoxLayout()
        self._widget = PyQt5.QtWidgets.QWidget()
        self._widgets = []
        flexes = []
        for child in self._children:
            widget = child.paintWidget()
            self._layout.addWidget(widget)
            self._widgets.append(widget)
            if isinstance(child, Expanded):
                flex = child._flex
            else:
                flex = 0
            flexes.append(flex)
        for i, flex in enumerate(flexes):
            self._layout.setStretch(i, flex)
        self._widget.setLayout(self._layout)
        return self._widget
    pass


class Column(Widget):
    """ Vertical alignment, wraps AxisAlignedBox. """
    def __init__(self, key: Key = Key(), children: List[Widget] = [],
                 alignment: Alignment = Alignment.none):
        super(Column, self).__init__(key)
        self._children = children
        self._alignment = alignment
        return

    def build(self, context: BuildContext):
        super(Column, self).build(context)
        self._child = AxisAlignedBox(
            children=self._children,
            vertical=True,
            alignment=self._alignment
        )
        self._child.build(context)
        self._hash = hash('Column(%d)' % self._child._hash)
        return

    def paintWidget(self) -> Any:
        return self._child.paintWidget()
    pass


class Row(Widget):
    """ Horizontal alignment, wraps AxisAlignedBox. """
    def __init__(self, key: Key = Key(), children: List[Widget] = [],
                 alignment: Alignment = Alignment.none):
        super(Row, self).__init__(key)
        self._children = children
        self._alignment = alignment
        return

    def build(self, context: BuildContext):
        super(Row, self).build(context)
        self._child = AxisAlignedBox(
            children=self._children,
            vertical=False,
            alignment=self._alignment
        )
        self._child.build(context)
        self._hash = hash('Row(%d)' % self._child._hash)
        return

    def paintWidget(self) -> Any:
        return self._child.paintWidget()
    pass


class TableView(Widget):
    """ A table showing items. The callback functions are:
    onSelect(row, col, oldData), onChanged(row, col, newData). """
    def __init__(self, key: Key = Key(), rows: int = 1, columns: int = 1,
                 headers: List[str] = [], data: List[List[str]] = [],
                 onSelected: Callable[[int, int, str], Any] = None,
                 onChanged: Callable[[int, int, str], Any] = None):
        super(TableView, self).__init__(key)
        self._rows = rows
        self._cols = columns
        self._headers = headers
        self._data = data
        self._onselected = onSelected
        self._onchanged = onChanged
        return

    def build(self, context: BuildContext):
        super(TableView, self).build(context)
        self._hash = hash('TableView(rows=%d,columns=%d,data=%s)' % (
            self._rows, self._cols, str(self._data)))
        return

    def _getdataitem(self, row: int, col: int) -> str:
        data = ''
        if row < len(self._data):
            if col < len(self._data[row]):
                data = str(self._data[row][col])
        return data

    def paintWidget(self) -> Any:
        self._widget = PyQt5.QtWidgets.QTableWidget()
        self._widget.setRowCount(self._rows)
        self._widget.setColumnCount(self._cols)
        # set data values
        for row in range(self._rows):
            for col in range(self._cols):
                data = self._getdataitem(row, col)
                self._widget.setItem(
                    row, col, PyQt5.QtWidgets.QTableWidgetItem(data))
                pass
            pass
        # set headers
        for i in range(self._cols):
            head = str(self._headers[i] if i < len(self._headers) else i + 1)
            self._widget.setHorizontalHeaderItem(
                i, PyQt5.QtWidgets.QTableWidgetItem(head))

        def onSelect(row, col):
            if self._onselected is not None:
                self._onselected(row, col, self._getdataitem(row, col))

        def onChanged(row, col):
            model = self._widget.model()
            idx = model.index(row, col)
            data = model.data(idx)
            if self._onchanged is not None:
                self._onchanged(row, col, data)
        self._widget.cellClicked.connect(onSelect)
        self._widget.cellChanged.connect(onChanged)
        return self._widget
    pass


class DropdownList(Widget):
    """ A dropdown list that you can choose items from. """
    def __init__(self, key: Key = Key(), items: List[str] = [], index: int = 0,
                 onChanged: Callable[[int, str], Any] = None):
        super(DropdownList, self).__init__(key)
        self._items = []
        for item in items:
            self._items.append(str(item))
        self._index = index
        self._onchanged = onChanged
        return

    def build(self, context: BuildContext):
        super(DropdownList, self).build(context)
        self._hash = hash('DropdownList(items=%s)' % ','.join(
            str(hash(i)) for i in self._items))
        return

    def paintWidget(self) -> Any:
        self._widget = PyQt5.QtWidgets.QComboBox()
        for item in self._items:
            self._widget.addItem(item)
        self._widget.setCurrentIndex(self._index)

        def onSelected(i):
            if self._onchanged is not None:
                self._onchanged(i, self._items[i])
        self._widget.currentIndexChanged.connect(onSelected)
        return self._widget
    pass


class Application:
    def __init__(self, context: Union[BuildContext, None] = None,
                 builder: Callable[[BuildContext], Widget] = None,
                 title: str = 'declPyQt5 Application',
                 width: int = None, height: int = None):
        """ The builder must accept a build context as input and output a
        full widget tree as an output. """
        if context is None:
            self._context = BuildContext(self)
        else:
            context._application = self
            self._context = context
        self._builder = builder
        self._title = title
        self._state = None
        self._running = False
        self._widget = None
        self._frame = None
        self._application = None
        self._windowsize = (width, height)
        return

    def setState(self) -> None:
        newState = self._builder(self._context)
        newState.build(self._context)
        oldWidget = self._layout.takeAt(0)
        oldWidget.widget().deleteLater()
        widget = newState.paintWidget()
        self._layout.addWidget(widget)
        return

    def run(self) -> None:
        if self._running:
            return
        self._state = self._builder(self._context)
        self._state.build(self._context)
        self._application = PyQt5.QtWidgets.QApplication([])
        self._widget = PyQt5.QtWidgets.QWidget()
        self._layout = PyQt5.QtWidgets.QHBoxLayout()
        widget = self._state.paintWidget()
        self._layout.addWidget(widget)
        self._widget.setLayout(self._layout)
        self._widget.setWindowTitle(self._title)
        if self._windowsize[0] is not None and self._windowsize[1] is not None:
            _width, _height = self._windowsize
            self._widget.resize(_width, _height)
        self._widget.show()
        self._application.exec_()
        return
    pass


class MessageBoxIcon(enum.Enum):
    none = 0
    question = 1
    info = 2
    warning = 3
    critical = 4


class MessageBoxButtons(enum.Enum):
    ok = 0
    okCancel = 1
    yesNo = 2
    close = 3


def showMessageBox(title: str = 'Message box', text: str = 'Message box',
                   icon: MessageBoxIcon = MessageBoxIcon.none,
                   buttons: MessageBoxButtons = MessageBoxButtons.ok,
                   onTap: Callable[[str], Any] = None):
    """ Displays message box. Use onTap to retrieve callback. """
    msg = PyQt5.QtWidgets.QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    qmb = PyQt5.QtWidgets.QMessageBox
    if icon != MessageBoxIcon.none:
        msg.setIcon({
            MessageBoxIcon.question: qmb.Question,
            MessageBoxIcon.info: qmb.Information,
            MessageBoxIcon.warning: qmb.Warning,
            MessageBoxIcon.critical: qmb.Critical,
        }[icon])
    _buttons = []

    def foo(button):
        if button == _buttons[0]:
            bid = {
                MessageBoxButtons.ok: 'ok',
                MessageBoxButtons.okCancel: 'ok',
                MessageBoxButtons.yesNo: 'yes',
                MessageBoxButtons.close: 'close',
            }[buttons]
        else:
            bid = {
                MessageBoxButtons.okCancel: 'cancel',
                MessageBoxButtons.yesNo: 'no',
            }[buttons]
        if onTap is not None:
            onTap(bid)
    if buttons == MessageBoxButtons.ok:
        msg.setStandardButtons(qmb.Ok)
        msg.buttonClicked.connect(foo)
    elif buttons == MessageBoxButtons.okCancel:
        msg.setStandardButtons(qmb.Ok | qmb.Cancel)
        msg.buttonClicked.connect(foo)
    elif buttons == MessageBoxButtons.yesNo:
        msg.setStandardButtons(qmb.Yes | qmb.No)
        msg.buttonClicked.connect(foo)
    elif buttons == MessageBoxButtons.close:
        msg.setStandardButtons(qmb.Close)
        msg.buttonClicked.connect(foo)
    _buttons = msg.buttons()
    msg.exec_()
    return

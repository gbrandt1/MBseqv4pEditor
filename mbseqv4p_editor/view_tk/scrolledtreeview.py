import logging
import os
from tkinter import *
from tkinter.ttk import *

from ..helpers import *
from .editabletreeview import *

logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class ScrolledTreeview(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        vsb = Scrollbar(self, orient="vertical")
        hsb = Scrollbar(self, orient="horizontal")

        self.tv = EditableTreeview(
            self,
            # columns=("fullpath", "type", "size"),
            # displaycolumns="size",
            # show='tree',
            selectmode=EXTENDED,
            yscrollcommand=lambda f, l: self.autoscroll(vsb, f, l),
            xscrollcommand=lambda f, l: self.autoscroll(hsb, f, l),
        )

        vsb["command"] = self.tv.yview
        hsb["command"] = self.tv.xview

        self.tv.grid(column=0, row=0, sticky="nswe")
        vsb.grid(column=1, row=0, sticky="ns")
        hsb.grid(column=0, row=1, sticky="ew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tv.tag_configure(
            "empty", foreground="gray60"
        )  # , font='TkFixedFont 14 italic')

        self.tv.bind("<Command-l>", lambda e: self.open_all(False))
        self.tv.bind("<Command-p>", lambda e: self.open_all())
        self.tv.bind("<Escape>", self.deselect_all)
        self.tv.bind("<Command-a>", lambda e: self.select_all())
        self.tv.bind("<Command-c>", lambda e: self.on_copy())
        self.tv.bind("<Command-v>", lambda e: self.on_paste())
        self.tv.bind("<Command-x>", lambda e: self.on_clear())

        self.tv.bind("<<TreeviewOpen>>", lambda e: self.on_open(e))
        self.tv.bind("<<TreeviewSelect>>", self.on_row_selected, add=True)
        self.tv.bind("<<TreeviewCellEdited>>", self.on_cell_changed)
        self.tv.bind("<<TreeviewInplaceEdit>>", self.on_row_edit)

    def populate_roots(self, num, iid, flabel=lambda x: x + 1):
        """(Re)populate root elements"""
        self.tv.delete(*self.tv.get_children())
        self.tv.heading("#0", text=iid.capitalize(), anchor=W)
        for n in range(num):
            item = f"{iid}{n:03}"
            text = f"{flabel(n):2}"
            self.tv.insert("", "end", item)
            self.tv.item(item, text=text, tag="empty")

    def populate_node(self, node, num, iid, flabel=lambda x: x + 1):
        self.tv.delete(*self.tv.get_children(node))
        for n in range(num):
            item = f"{node}_{iid}{n:03}"
            # text=f'{label}{char(n):2}'
            text = f"{flabel(n):2}"
            # print(text)
            self.tv.insert(node, "end", item)
            self.tv.item(item, text=text, tag="empty")

    def autosize_columns(self):
        self.tv.column("#0", stretch=0, width=2 * measure_str("track000"))
        vmax = [0] * 8
        for item in self.tv.get_children():
            values = self.tv.item(item)["values"]
            # print(values)
            for col, v in enumerate(values):
                if len(str(v)) > vmax[col]:
                    vmax[col] = measure_str(v)
        # logger.info(f'autosize_columns {vmax}')
        for n, col in enumerate(self.tv["columns"]):
            # print(col, vmax[n])
            # self.tv.column(col, width = vmax[n])
            self.tv.column(col, minwidth=int(vmax[n] * 1.4))

    def on_open(self, event):
        tv = event.widget
        item = tv.focus()
        logger.debug(f"on_open {item}")

    ##def on_select(self, event):
    #    tv = event.widget
    #    item = tv.focus()
    #    logger.debug(f'on_select {item}')

    def on_copy():
        logger.info("on_copy")

    def on_paste():
        logger.info("on_paste")

    def on_clear():
        logger.info("on_clear")

    def on_row_selected(self, event):
        logger.debug(f"on_row_selected {event.widget.selection()}")
        for item in self.tv.selection():
            for item2 in self.tv.get_children(item):
                if item2 not in self.tv.selection():
                    self.tv.selection_add(item2)

    def on_click(self, event):
        tv = event.widget
        item = tv.focus()
        logger.debug(f"on_click {item}")

    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(first, last)

    # Hooks from EditableTreeview
    def on_cell_changed(self, event):
        (col, item) = self.tv.get_event_info()
        logger.info(f"Column {col} of item {item} was changed")
        values = self.tv.item(item, "values")
        logger.debug(f"{item} {values}")

    def on_row_edit(self, event):
        col, item = self.tv.get_event_info()
        logger.debug(f"on_row_edit {col} {item}")
        # self.tv.inplace_entry(col, item)
        # self.tv.inplace_spinbox(col, item, 0, 127, 1)

    def deselect_all(self, parent=None):
        for item in self.tv.selection():
            self.tv.selection_remove(item)

    def select_all(self, parent=None):
        for item in self.tv.get_children(parent):
            logger.debug(f"select_all {item}")
            self.tv.selection_add(item)
            self.select_all(item)

    def open_all(self, o=True, parent=None):
        for item in self.tv.get_children(parent):
            self.tv.item(item, open=o)
            self.open_all(o, item)

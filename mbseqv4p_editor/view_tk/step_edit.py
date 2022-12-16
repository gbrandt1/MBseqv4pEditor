import logging
import os
from random import random
from pprint import pprint

from tkinter import *
from tkinter.ttk import *
from tkinter import font

from ..helpers import *
from ..layers import trg_layer_str
from ..track_cc import *
from .editabletreeview import *
from ..step_buffer import *


logger = logging.getLogger(f"{__name__:{LOGW_NAME}}")


class TVStepEditor(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.pack(fill=BOTH, expand=TRUE)
        self.controller = controller
        self.buf = StepBuffer()
        self.page_size = self.buf.page_size

        # State
        self.track_name = StringVar()
        self.xv = 0
        self.xv_max = 0
        self.allow_edit = BooleanVar(value=True)
        self.par_visible = BooleanVar(value=True)
        self.trg_visible = BooleanVar(value=True)
        self.wrap = BooleanVar(value=False)
        self.raw = BooleanVar(value=False)
        self.selection_ = []
        self.item_ = None

        # Widgets
        frm_tb = self.init_toolbar(self)
        frm_tv = self.init_treeview(self)

        frm_tb.pack(fill=X)  # , expand=TRUE)
        frm_tv.pack(fill=BOTH, expand=TRUE)

        self.connect_callbacks()

    def set_track(self, track):
        if not track:
            return
        self.buf.set_track(track)
        self.track_name.set(self.buf.track.name)
        self.num_steps = self.buf.num_steps
        self.update_view()
        self.open_all()

    def init_treeview(self, parent):
        # to do: replace by scrolledtreeview
        frm_tv = Frame(parent, padding=2)
        self.vsb = Scrollbar(frm_tv, orient=VERTICAL)
        self.hsb = Scrollbar(frm_tv, orient=HORIZONTAL)
        self.tv = EditableTreeview(
            frm_tv, selectmode=EXTENDED, yscrollcommand=self.vsb.set
        )
        self.tv["columns"] = [f"#{i+1}" for i in range(self.page_size)]
        self.tv.column("#0", stretch=0, width=160)
        for i in range(self.page_size):
            self.tv.column(
                f"#{i+1}",
                # stretch=False,
                width=60,  # self.tv.cget('font').measure('\u2588'*4),
                anchor=W,
            )
            self.tv.heading(f"#{i+1}", text=f"{i+2}")
        # self.tv.tag_configure('inst', )
        # self.tv.tag_configure('par', background='pale green',)
        # self.tv.tag_configure('trg', background='light steel blue',)
        # palegreen') #alice blue')
        self.tv.tag_configure("odd", background="#C0FFC0")  # 'lightgrey')
        # 'mintcream') #alice blue')
        self.tv.tag_configure("even", background="#E0FFE0")  # 'gainsboro')
        self.vsb.config(command=self.tv.yview)
        self.hsb.config(command=self.xview)
        self.tv.grid(column=0, row=0, sticky="nsew")
        self.vsb.grid(column=1, row=0, sticky="ns")
        self.hsb.grid(column=0, row=1, sticky="ew")
        frm_tv.grid_columnconfigure(0, weight=1)
        frm_tv.grid_rowconfigure(0, weight=1)
        return frm_tv

    def init_toolbar(self, parent):
        self.tool_widgets = {}
        bf = Frame(parent, padding=2)
        buttons = (
            (Button, "\u25B7", lambda: self.open_all(False), None, 2),
            (Button, "\u25BD", lambda: self.open_all(), None, 2),
            # (Button, 'Select All', lambda: self.select_all(), None),
            (Checkbutton, "Show Pars", self.update_view, self.par_visible, 6),
            (Checkbutton, "Show Trgs", self.update_view, self.trg_visible, 6),
            (Button, "\u25C0", self.left_key, None, -1),
            (Button, "\u25B6", self.right_key, None, -1),
            # (Checkbutton, 'Allow Edit', lambda: None, self.allow_edit),
            (Checkbutton, "Wrap", self.update_view, self.wrap, 0),
            (Checkbutton, "Raw", self.update_view, self.raw, 0),
            (Button, "Clear", self.clear_row, None, -1),
            (Button, "Random", self.random_row, None, -1),
        )
        for widget, name, cmd, var, ul in buttons:
            btn = widget(bf, text=name, command=cmd, variable=var, underline=ul)
            btn.pack(side=LEFT)
            self.tool_widgets[name] = btn
        self.scale = Scale(
            bf,
            from_=0.0,
            to=100.0,
            orient=HORIZONTAL,
            value=50.0,
        )
        self.scale.pack(side=LEFT)
        return bf

    def connect_callbacks(self):
        self.tv.bind(
            "<MouseWheel>", lambda event: self.tv.yview("scroll", -event.delta, "units")
        )
        self.tv.bind(
            "<Shift-MouseWheel>",
            lambda event: self.xview("scroll", -event.delta, "units"),
        )
        self.tv.bind("<Command-l>", lambda e: self.open_all(False))
        self.tv.bind("<Command-p>", lambda e: self.open_all())
        self.tv.bind("<Escape>", self.deselect_all)
        self.tv.bind("<Command-a>", lambda e: self.select_all())
        self.tv.bind("<Command-w>", lambda e: self.tool_widgets["Wrap"].invoke())
        self.tv.bind("<Command-r>", lambda e: self.tool_widgets["Raw"].invoke())
        self.tv.bind("<Command-Left>", self.left_key, add=True)
        self.tv.bind("<Command-Right>", self.right_key, add=True)
        self.tv.bind("<Double-1>", self.on_double_click)  # , add=True)
        self.tv.bind("<<TreeviewSelect>>", self.on_row_selected, add=True)
        self.tv.bind("<<TreeviewCellEdited>>", self.on_cell_changed)
        self.tv.bind("<<TreeviewInplaceEdit>>", self.on_row_edit)

    # Treeview items

    def populate_items(self):
        """Init items for new track"""
        logger.debug(f"populate_items")
        # Save open state in case only view changes but not track
        open_state = {}
        for i in self.tv.get_children():
            open_state[i] = self.tv.item(i)["open"]
        self.tv.delete(*self.tv.get_children())
        self.populate_instruments()
        self.populate_layers()
        if self.wrap.get():
            self.populate_pages()
        # Restore open state
        for i in self.tv.get_children():
            if i in open_state:
                self.tv.item(i, open=open_state[i])

    def populate_instruments(self):
        """Instrument Names"""
        if not self.buf.track:
            return
        for pi in range(self.buf.track.num_p_instruments):
            if self.buf.track.event_mode == "Drum":
                drumname = f"{self.track_name.get()[5*pi:5*pi+5]}"
            else:
                drumname = ""
            self.tv.insert(
                "",
                "end",
                f"inst{pi:02}",
                # text=f'Inst {pi+1} {drumname}',
                text=drumname,
                tag="inst",
            )

    def populate_layers(self):
        def insert_layer_item(item, **kwargs):
            l = int(item[10:12])
            if "par" in item:
                name = self.buf.par_layer_types[l]["name"]
                blk = "Par"
            else:
                name = self.buf.trg_layer_names[l]
                blk = "Trg"
            self.tv.insert(
                item[:6],
                "end",
                item,
                text=name,
                tag=blk.lower(),
            )

        if self.par_visible.get():
            self.buf.for_all_pars(insert_layer_item)
        if self.trg_visible.get():
            self.buf.for_all_trgs(insert_layer_item)

    def populate_pages(self):
        def insert_page_item(item, **kwargs):
            # logger.info(f'insert_page_item {item[:-7]} {item}')
            i, l, pg = item2ilp(item)
            text = f"Step {pg*self.page_size+1:3}-{(pg+1)*self.page_size:3}"
            self.tv.insert(
                item[:-7], "end", item, text=text, tag="even" if pg % 2 else "odd"
            )

        self.buf.for_all_pars(
            self.buf.for_all_pages, row_func=insert_page_item
        )  # , force=True)
        self.buf.for_all_trgs(
            self.buf.for_all_pages, row_func=insert_page_item
        )  # , force=True)

    def show_visible_pages(self):
        for c in range(self.page_size):
            self.tv.heading(
                f"#{c+1}",
                text=f"{c+self.xv+1}",
            )
        self.buf.for_all_pars(self.show_row)
        self.buf.for_all_trgs(self.show_row)

    def get_visible_item(self, item):
        """Get item of visible page in case of scroll view."""
        i, l, p = item2ilp(item)
        blk = item2blk(item)
        if not blk:
            # instrument row - show nothing
            return False
        # in case of trg/par header row copy visible page
        if not self.wrap.get():
            npage = self.xv // self.page_size
            if blk == "par":
                npage = npage % self.buf.num_par_pages
            vitem = item + f"_page{npage:02}"
            # logger.info(f'get_visible_item: {item} --> {vitem}')
            return vitem
        return item

    def show_all_pages(self):
        self.buf.for_all_pars(self.buf.for_all_pages, row_func=self.show_row)
        self.buf.for_all_trgs(self.buf.for_all_pages, row_func=self.show_row)

    def show_row(self, item, offset=0):
        """Copy Representation of row from buffer of values to TV items"""
        blk = item2blk(item)
        if not blk:
            # instrument row - show nothing
            return
        if not self.wrap.get():
            if "page" in item:
                return
            vitem = self.get_visible_item(item)
            values = self.buf.values[vitem]
        else:
            if not "page" in item:
                return
            values = self.buf.values[item]
        i, l, p = item2ilp(item)
        if not self.raw.get():
            if blk == "par":
                values = [self.buf.par_layer_types[l]["str"](v) for v in values]
            else:
                values = [trg_layer_str(v) for v in values]
        if not self.wrap.get():
            tag = "even" if l % 2 else "odd"
        # logger.info(f'show_row: {item} {offset} {values}')
        self.tv.item(item, values=values)

    def update_view(self):
        """Complete Redraw"""
        logger.debug(f"update_view {self.wrap.get()}")
        # sel = self.tv.selection()
        self.populate_items()
        # self.buf.set_all_pages_from_track()
        if self.wrap.get():
            self.hsb.grid_remove()
            self.show_all_pages()
        else:
            self.hsb.grid()
            # self.set_visible_page()
            self.show_visible_pages()
        self.open_all()
        # self.tv.selection_add(sel)

    # Editing callbacks

    def on_row_selected(self, event):
        # logger.info(f'on_row_selected {event.widget.selection()}')

        # for item in self.selection_:
        # Update view of previous selection
        # logger.info(f'on_row_selected update previous view {self.selection_}')
        # print(self.buf.values)
        # self.show_visible_page(item)
        #    self.show_row(item)
        # self.selection_ = None

        for item in self.tv.selection():
            for item2 in self.tv.get_children(item):
                if item2 not in self.tv.selection():
                    self.tv.selection_add(item2)
        # logger.info(f'on_row_selected {self.tv.selection()}')

        # keep previous selection
        # self.selection_=list(self.tv.selection())

    def on_cell_changed(self, event):
        col, item = self.tv.get_event_info()
        values = self.tv.item(item, "values")
        logger.info(f"on_cell_changed {item} {col:3}: {values}")
        # i, l, p = item2ilp(item)
        # s0 = self.xv
        # self.buf.values_[item] = values
        self.item_ = item
        if not self.wrap.get():
            blk = item2blk(item)
            npage = self.xv // self.page_size
            if blk == "par":
                npage = npage % self.buf.num_par_pages
            item = item + f"_page{npage:02}"
            # self.buf.values[vitem] = self.buf.values[item]
        self.buf.values_[item] = list(values)
        self.buf.update_changed_values()
        # self.show_row(item)
        # self.update_view()

    def on_row_edit(self, event):
        """Set up inplace widgets for editing.
        Called for every column
        """
        if not self.allow_edit.get():
            return
        if self.item_:
            logger.info(f"on_row_edit show last {self.item_}")
            self.show_row(self.item_)
            self.item_ = None
        col, item = self.tv.get_event_info()
        if not "par" in item:
            return
        if self.wrap.get() and not "page" in item:
            return
        if item not in self.buf.values:
            vitem = self.get_visible_item(item)
            values = self.buf.values[vitem]
        else:
            values = self.buf.values[item]
        if col == "#0":
            logger.info(f"on_row_edit {item} {col:3}: {values}")
            return
        # Copy numerical values over representations
        self.tv.item(item, values=values)
        self.tv.inplace_spinbox(col, item, 0, 127, 1)

    # Double click edit for triggers - always active
    def on_double_click(self, event):
        # for item in self.tv.selection():
        col, item = self.tv.get_event_info()
        if not "trg" in item:
            return
            # continue
        # values = self.buf.values[item]
        # item_text = list(self.tv.item(item, "values"))
        col = self.tv.identify_column(event.x)
        logger.info(f"on_double_click {col} {item}")
        cn = int(str(col).replace("#", "")) - 1
        if not "page" in item:
            vitem = self.get_visible_item(item)
        else:
            vitem = item
        self.buf.values_[vitem] = self.buf.values[vitem]
        self.buf.values_[vitem][cn] = 0 if self.buf.values[vitem][cn] else 1
        print(self.buf.values_[vitem])
        self.buf.update_changed_values()
        # self.update_view()
        self.show_row(item)
        # row = self.tv.identify_row(event.y)
        # s = item_text[cn]
        # s = '\u25CF' if s == '\u25CB' else '\u25CB'  # '\u00B7' else '\u00B7'
        # item_text[cn] = s
        # self.tv.item(item, values=self.buf.values[item])

    def _edit_row(self, func):
        for item in self.tv.selection():
            blk = item2blk(item)
            if not blk:
                continue
            if not self.wrap.get():
                if "page" in item:
                    continue
                vitem = self.get_visible_item(item)
            else:
                if not "page" in item:
                    continue
                vitem = item
            # i, l, p = item2ilp(item)
            # if self.wrap.get():
            #    if not 'page' in item:
            #        continue
            #    s0 = p*self.page_size
            #    s1 = (p+1)*self.page_size
            # else:
            #    if 'page' in item:
            #        continue
            #    if 'par' not in item and 'trg' not in item:
            #        continue
            #    s0 = self.xv*self.page_size
            #    s1 = (self.xv+1)*self.page_size
            values = [func(vitem) for s in range(self.page_size)]
            print(f"{vitem} {values}")
            self.buf.values_[vitem] = values
            self.buf.update_changed_values()
            # self.show_all_pages()
            self.show_row(item)
        # self.tv.item(item, values=values)
        # --> move to controller
        # for s in range(s0, s1):
        #    if 'trg' in item:
        #        self.track.trg_set(s, l, i, values[s-s0])
        #    if 'par' in item:
        #        self.track.par_set(s, l, i, values[s-s0])
        # self.track.modified()

    def clear_row(self):
        def clear_func(item):
            if "trg" in item:
                return 0  # '\u00B7'
            if "par" in item:
                i, l, p = item2ilp(item)
                d = self.buf.par_layer_types[l]["default"]
                # d = dl[l]
                return d

        self._edit_row(clear_func)

    def random_row(self):
        r = self.scale.get() / 100.0
        logger.debug(f"random_row {r}")

        def random_func(item):
            # print(r)
            if "trg" in item:
                # return '\u00B7' if random() > r else '\u25CF'
                return 1 if random() > r else 0
            if "par" in item:
                i, l, p = item2ilp(item)
                m = self.buf.par_layer_types[l]["max"]
                d = random() * m * r
                return int(d)

        self._edit_row(random_func)

    def xview(self, *args):
        if self.wrap.get():
            return
        # num_steps = self.track.num_trg_steps
        # print('xview',*args)
        if args[0] == "moveto":
            page = int(float(args[1]) * self.num_pages)
            self.xv = page * self.page_size
        if args[0] == "scroll":
            self.xv += self.page_size * int(args[1])
        self.xv = max(min(self.num_steps - self.page_size, self.xv), 0)
        xmin = float(self.xv) / self.num_steps
        xmax = (self.xv + self.page_size) / self.num_steps
        # print(xmin,xmax)
        self.hsb.set(xmin, xmax)
        self.show_visible_pages()
        # set_visible_page()

    def left_key(self, event=None):
        if self.wrap.get():
            return
        # print("Left")
        if self.xv > 0:
            self.xv -= self.page_size
        # self.set_visible_page()
        self.show_visible_pages()
        self.xview("moveto", self.xv / self.num_steps)
        return "break"

    def right_key(self, event=None):
        if self.wrap.get():
            return
        # print("Right")
        if self.xv < self.buf.track.num_trg_steps - self.page_size:
            self.xv += self.page_size
        # self.set_visible_page()
        self.show_visible_pages()
        self.xview("moveto", self.xv / self.num_steps)
        return "break"

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

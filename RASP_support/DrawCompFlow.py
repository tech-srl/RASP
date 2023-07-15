from FunctionalSupport import Unfinished, guarded_contains, base_tokens, \
    tokens_asis
from Support import clean_val
import os
import string

# fix: in ordering, we always connect bottom FF to top select. but sometimes,
# there is no FF (if go straight into next select), or there is no rendered
# select (in special case of full-select)

layer_color = 'lemonchiffon'
head_color = 'bisque'  # 'yellow'

indices_colour = 'bisque3'
comment_colour = 'cornsilk'
select_on_colour = 'plum'
select_off_colour = head_color


def windows_path_cleaner(s):
    if os.name == "nt":  # is windows
        validchars = "-_.() "+string.ascii_letters+string.digits

        def fix(c):
            return c if c in validchars else "."
        return "".join([fix(c) for c in s])
    else:
        return s


def colour_scheme(row_type):
    if row_type == INPUT:
        return 'gray', 'gray', 'gray'
    if row_type == QVAR:
        return 'palegreen4', 'mediumseagreen', 'palegreen1'
    elif row_type == KVAR:
        return 'deepskyblue3', 'darkturquoise', 'darkslategray1'
    elif row_type == VVAR:
        return 'palevioletred3', 'palevioletred2', 'lightpink'
    elif row_type == VREAL:
        return 'plum4', 'plum3', 'thistle2'
    elif row_type == RES:
        return 'lightsalmon3', 'burlywood', 'burlywood1'
    else:
        raise Exception("unknown row type: "+str(row_type))


QVAR, KVAR, VVAR, VREAL, RES, INPUT = [
    "QVAR", "KVAR", "VVAR", "VREAL", "RES", "INPUT"]
POSS_ROWS = [QVAR, KVAR, VVAR, VREAL, RES, INPUT]
ROW_NAMES = {QVAR: "Me", KVAR: "Other", VVAR: "X",
             VREAL: "f(X)", RES: "FF", INPUT: ""}


def UnfinishedFunc(f):
    setattr(Unfinished, f.__name__, f)


@UnfinishedFunc
def last_val(self):
    return self.last_res.get_vals()


def makeQKStable(qvars, kvars, select, ref_in_g):
    qvars = [q.last_val() for q in qvars]
    kvars = [k.last_val() for k in kvars]
    select = select.last_val()
    q_val_len, k_val_len = len(select), len(select[0])

    qvars_skip = len(kvars)
    kvars_skip = len(qvars)
    _, _, qvars_colour = colour_scheme(QVAR)
    _, _, kvars_colour = colour_scheme(KVAR)
    # select has qvars along the rows and kvars along the columns, so we'll do
    # the same. i.e. top rows will just be the kvars and first columns will
    # just be the qvars if (not qvars) and (not kvars): # no qvars or kvars ->
    # full select -> dont waste space drawing
    # 	num_rows, num_columns = 0, 0
    # 	pass
    # else:
    # 	num_rows = qvars_skip+(len(qvars[0]) if qvars else 1)
    # 	num_columns = kvars_skip+(len(kvars[0]) if kvars else 1)
    num_rows = qvars_skip+q_val_len
    num_columns = kvars_skip+k_val_len

    select_cells = {i: [CellVals('', head_color, j, i)
                        for j in range(num_columns)]
                    for i in range(num_rows)}

    for i, seq in enumerate(kvars):
        for j, v in enumerate(seq):
            vals = CellVals(v, kvars_colour, i, j+kvars_skip)
            select_cells[i][j + kvars_skip] = vals
    for j, seq in enumerate(qvars):
        for i, v in enumerate(seq):
            vals = CellVals(v, qvars_colour, i+qvars_skip, j)
            select_cells[i + qvars_skip][j] = vals

    for i in range(num_rows-qvars_skip):  # i goes over the q_var values
        for j in range(num_columns-kvars_skip):  # j goes over the k_var values
            v = select[i][j]
            colour = select_on_colour if v else select_off_colour
            select_cells[i+qvars_skip][j+kvars_skip] = CellVals(
                v, colour, i+qvars_skip, j+kvars_skip, select_internal=True)

    # TODO: make an ugly little q\k triangle thingy in the top corner
    return GridTable(select_cells, ref_in_g)


class CellVals:
    def __init__(self, val, colour, i_row, i_col, select_internal=False,
                 known_portstr=None):
        def mystr(v):
            if isinstance(v, bool):
                if select_internal:
                    return ' ' if v else ' '  # color gives it all!
                else:
                    return 'T' if v else 'F'
            if isinstance(v, float):
                v = clean_val(v, 3)
            if isinstance(v, int) and len(str(v)) == 1:
                v = " "+str(v)  # for pretty square selectors
            return str(v).replace("<", "&#60;").replace(">", "&#62;")
        self.val = mystr(val)
        self.colour = colour
        if None is known_portstr:
            self.portstr = "_col"+str(i_col)+"_row"+str(i_row)
        else:
            self.portstr = known_portstr

    def __str__(self):
        return '<td bgcolor="' + self.colour + '" PORT="' + self.portstr \
            + '">' + self.val+'</td>'


class GridTable:
    def __init__(self, cellvals, ref_in_g):
        self.ref_in_g = ref_in_g
        self.cellvals = cellvals
        self.numcols = len(cellvals.get(0, []))
        self.numrows = len(cellvals)
        self.empty = 0 in [self.numcols, self.numrows]

    def to_str(self, transposed=False):
        ii = sorted(list(self.cellvals.keys()))
        rows = [self.cellvals[i] for i in ii]

        def cells2row(cells):
            return '<tr>'+''.join(map(str, cells))+'</tr>'
        return '<<table cellspacing="0">' + ''.join(map(cells2row, rows)) \
            + '</table>>'

    def bottom_left_portstr(self):
        return self.access_portstr(0, -1)

    def bottom_right_portstr(self):
        return self.access_portstr(-1, -1)

    def top_left_portstr(self):
        return self.access_portstr(0, 0)

    def top_right_portstr(self):
        return self.access_portstr(-1, 0)

    def top_access_portstr(self, i_col):
        return self.access_portstr(i_col, 0)

    def bottom_access_portstr(self, i_col):
        return self.access_portstr(i_col, -1)

    def access_portstr(self, i_col, i_row):
        return self.ref_in_g + ":" + self.internal_portstr(i_col, i_row)

    def internal_portstr(self, i_col, i_row):
        if i_col < 0:
            i_col = self.numcols + i_col
        if i_row < 0:
            i_row = self.numrows + i_row
        return "_col"+str(i_col)+"_row"+str(i_row)

    def add_to_graph(self, g):
        if self.empty:
            pass
        else:
            g.node(name=self.ref_in_g, shape='none',
                   margin='0', label=self.to_str())


class Table:
    def __init__(self, seqs_by_rowtype, ref_in_g, rowtype_order=[]):
        self.ref_in_g = ref_in_g
        # consistent presentation, and v useful for feedforward clarity
        self.rows = []
        self.seq_index = {}
        if len(rowtype_order) > 1:
            self.add_rowtype_cell = True
        else:
            assert len(seqs_by_rowtype.keys(
            )) == 1, "table got multiple row types but no order for them"
            rowtype_order = list(seqs_by_rowtype.keys())
            self.add_rowtype_cell = not (rowtype_order[0] == RES)
        self.note_res_dependencies = len(seqs_by_rowtype.get(RES, [])) > 1
        self.leading_metadata_offset = 1 + self.add_rowtype_cell
        for rt in rowtype_order:
            seqs = sorted(seqs_by_rowtype[rt],
                          key=lambda seq: seq.creation_order_id)
            for i, seq in enumerate(seqs):
                # each one appends to self.rows.
                self.n = self.add_row(seq, rt)
                # self.n stores length of a single row, they will all be the
                # same, just easiest to get like this
                # add_row has to happen one at a time b/c they care about
                # length of self.rows at time of addition (to get ports right)
        self.empty = len(self.rows) == 0
        if self.empty:
            self.n = 0
        # (len(rowtype_order)==1 and rowtype_order[0]==QVAR)
        self.transpose = False
        # no need to twist Q, just making the table under anyway
        # transpose affects the port accesses, but think about that later

    def to_str(self):
        rows = self.rows if not self.transpose else list(zip(*self.rows))

        def cells2row(cells):
            return '<tr>'+''.join(cells)+'</tr>'
        return '<<table cellspacing="0">' + ''.join(map(cells2row, rows)) \
            + '</table>>'

    def bottom_left_portstr(self):
        return self.access_portstr(0, -1)

    def bottom_right_portstr(self):
        return self.access_portstr(-1, -1)

    def top_left_portstr(self):
        return self.access_portstr(0, 0)

    def top_right_portstr(self):
        return self.access_portstr(-1, 0)

    def top_access_portstr(self, i_col, skip_meta=False):
        return self.access_portstr(i_col, 0, skip_meta=skip_meta)

    def bottom_access_portstr(self, i_col, skip_meta=False):
        return self.access_portstr(i_col, -1, skip_meta=skip_meta)

    def access_portstr(self, i_col, i_row, skip_meta=False):
        return self.ref_in_g + ":" + self.internal_portstr(i_col, i_row,
                                                           skip_meta=skip_meta)

    def internal_portstr(self, i_col, i_row, skip_meta=False):
        if skip_meta and (i_col >= 0):  # before flip things for reverse column
            # access
            i_col += self.leading_metadata_offset
        if i_col < 0:
            i_col = (self.n) + i_col
        if i_row < 0:
            i_row = len(self.rows) + i_row
        return "_col"+str(i_col)+"_row"+str(i_row)

    def add_row(self, seq, row_type):
        def add_cell(val, colour):
            res = CellVals(val, colour, -1, -1,
                           known_portstr=self.internal_portstr(len(cells),
                                                               len(self.rows)))
            cells.append(str(res))

        def add_strong_line():
            # after failing to inject css styles in graphviz,
            # seeing that their <VR/> suggestion only creates lines
            # (if at all? unclear) of width 1
            # (same as the border already there) and it wont make multiple VRs,
            # and realising their <columns> suggestion also does nothing,
            # refer to hack at the top of this priceless page:
            # http://jkorpela.fi/html/cellborder.html
            cells.append('<td bgcolor="black" width="0"></td>')

        qkvr_colour, name_colour, data_colour = colour_scheme(row_type)
        cells = []  # has to be created in advance, and not just be all the
        # results of add_cell, because add_cell cares about current length of
        # 'cells'
        if self.add_rowtype_cell:
            add_cell(ROW_NAMES[row_type], qkvr_colour)
        add_cell(seq.name, name_colour)
        for v in seq.last_val():
            add_cell(v, data_colour)
        if self.note_res_dependencies:
            self.seq_index[seq] = len(self.rows)
            add_strong_line()
            add_cell("("+str(self.seq_index[seq])+")", indices_colour)
            add_cell(self.dependencies_str(seq, row_type), comment_colour)
        self.rows.append(cells)
        return len(cells)

    def dependencies_str(self, seq, row_type):
        if not row_type == RES:
            return ""
        return "from ("+", ".join(str(self.seq_index[m]) for m in
                                  seq.get_nonminor_parent_sequences()) + ")"

    def add_to_graph(self, g):
        if self.empty:
            # g.node(name=self.ref_in_g,label="empty table")
            pass
        else:
            g.node(name=self.ref_in_g, shape='none',
                   margin='0', label=self.to_str())


def place_above(g, node1, node2):

    g.edge(node1.bottom_left_portstr(), node2.top_left_portstr(),
           style="invis")
    g.edge(node1.bottom_right_portstr(),
           node2.top_right_portstr(), style="invis")


def connect(g, top_table, bottom_table, select_vals):
    # connects top_table as k and bottom_table as q
    if top_table.empty or bottom_table.empty:
        return  # not doing this for now
    place_above(g, top_table, bottom_table)
    # just to position them one on top of the other, even if select is empty
    for q_i in select_vals:
        for k_i, b in enumerate(select_vals[q_i]):
            if b:
                # have to add 2 cause first 2 are data type and row name
                g.edge(top_table.bottom_access_portstr(k_i, skip_meta=True),
                       bottom_table.top_access_portstr(q_i, skip_meta=True),
                       arrowhead='none')


class SubHead:
    def __init__(self, name, seq):
        vvars = seq.get_immediate_parent_sequences()
        if not seq.definitely_uses_identity_function:
            vreal = seq.pre_aggregate_comp()
            vreal(seq.last_w)  # run it on same w to fill with right results
            vreals = [vreal]
        else:
            vreals = []

        self.name = name
        self.vvars_table = Table(
            {VVAR: vvars, VREAL: vreals}, self.name+"_vvars",
            rowtype_order=[VVAR, VREAL])
        self.res_table = Table({RES: [seq]}, self.name+"_res")
        self.default = "default: " + \
            str(seq.default) if seq.default is not None else ""
        # self.vreals_table =  ## ? add partly processed vals, useful for eg
        # conditioned_contains?

    def add_to_graph(self, g):
        self.vvars_table.add_to_graph(g)
        self.res_table.add_to_graph(g)
        if self.default:
            g.node(self.name+"_default", shape='rectangle', label=self.default)
            g.edge(self.name+"_default", self.res_table.top_left_portstr(),
                   arrowhead='none')

    def add_edges(self, g, select_vals):
        connect(g, self.vvars_table, self.res_table, select_vals)

    def bottom_left_portstr(self):
        return self.res_table.bottom_left_portstr()

    def bottom_right_portstr(self):
        return self.res_table.bottom_right_portstr()

    def top_left_portstr(self):
        return self.vvars_table.top_left_portstr()

    def top_right_portstr(self):
        return self.vvars_table.top_right_portstr()


class Head:
    def __init__(self, name, head_primitives, i):
        self.name = name
        self.i = i
        self.head_primitives = head_primitives
        select = self.head_primitives.select
        q_vars, k_vars = select.q_vars, select.k_vars
        q_vars = sorted(list(set(q_vars)), key=lambda a: a.creation_order_id)
        k_vars = sorted(list(set(k_vars)), key=lambda a: a.creation_order_id)
        self.kq_table = Table({QVAR: q_vars, KVAR: k_vars},
                              self.name+"_qvars", rowtype_order=[KVAR, QVAR])
        # self.k_table = Table({KVAR:k_vars},self.name+"_kvars")
        self.select_result_table = makeQKStable(
            q_vars, k_vars, select, self.name+"_select")
        # self.select_table = SelectTable(self.head_primitives.select,
        #                                 self.name+"_select")
        self.subheads = [SubHead(self.name+"_subcomp_"+str(i), seq)
                         for i, seq in
                         enumerate(self.head_primitives.sequences)]

    def add_to_graph(self, g):
        with g.subgraph(name=self.name) as head:
            def headlabel():
                # return self.head_primitives.select.name
                return 'head '+str(self.i) +\
                    "\n("+self.head_primitives.select.name+")"
            head.attr(fillcolor=head_color, label=headlabel(),
                      fontcolor='black', style='filled')
            with head.subgraph(name=self.name+"_select_parts") as sel:
                sel.attr(rankdir="LR", label="", style="invis", rank="same")
                if True:  # not (self.kq_table.empty):
                    self.select_result_table.add_to_graph(sel)
                    self.kq_table.add_to_graph(sel)
                    # sel.edge(self.kq_table.bottom_right_portstr(),
                    # self.select_result_table.bottom_left_portstr(),style="invis")

            [s.add_to_graph(head) for s in self.subheads]

    def add_organising_edges(self, g):
        if self.kq_table.empty:
            return
        for s in self.subheads:
            place_above(g, self.select_result_table, s)

    def bottom_left_portstr(self):
        return self.subheads[0].bottom_left_portstr()

    def bottom_right_portstr(self):
        return self.subheads[-1].bottom_right_portstr()

    def top_left_portstr(self):
        if not (self.kq_table.empty):
            return self.kq_table.top_left_portstr()
        else:  # no kq (and so no select either) table. go into subheads
            return self.subheads[0].top_left_portstr()

    def top_right_portstr(self):
        if not (self.kq_table.empty):
            return self.kq_table.top_right_portstr()
        else:
            return self.subheads[-1].top_right_portstr()

    def add_edges(self, g):
        select_vals = self.head_primitives.select.last_val()
        # connect(g,self.k_table,self.q_table,select_vals)
        for s in self.subheads:
            s.add_edges(g, select_vals)
        self.add_organising_edges(g)


def contains_tokens(mvs):
    return next((True for mv in mvs if guarded_contains(base_tokens, mv)),
                False)


class Layer:
    def __init__(self, depth, d_heads, d_ffs, add_tokens_on_ff=False):
        self.heads = []
        self.depth = depth
        self.name = self.layer_cluster_name(depth)
        for i, h in enumerate(d_heads):
            self.heads.append(Head(self.name+"_head"+str(i), h, i))
        ff_parents = []
        for ff in d_ffs:
            ff_parents += ff.get_nonminor_parent_sequences()
        ff_parents = list(set(ff_parents))
        ff_parents = [p for p in ff_parents if not guarded_contains(d_ffs, p)]
        rows_by_type = {RES: d_ffs, VVAR: ff_parents}
        rowtype_order = [VVAR, RES]
        if add_tokens_on_ff and not contains_tokens(ff_parents):
            rows_by_type[INPUT] = [tokens_asis]
            rowtype_order = [INPUT] + rowtype_order
        self.ff_table = Table(rows_by_type, self.name+"_ffs", rowtype_order)

    def bottom_object(self):
        if not self.ff_table.empty:
            return self.ff_table
        else:
            return self.heads[-1]

    def top_object(self):
        if self.heads:
            return self.heads[0]
        else:
            return self.ff_table

    def bottom_left_portstr(self):
        return self.bottom_object().bottom_left_portstr()

    def bottom_right_portstr(self):
        return self.bottom_object().bottom_right_portstr()

    def top_left_portstr(self):
        return self.top_object().top_left_portstr()

    def top_right_portstr(self):
        return self.top_object().top_right_portstr()

    def add_to_graph(self, g):
        with g.subgraph(name=self.name) as s:
            s.attr(fillcolor=layer_color, label='layer '+str(self.depth),
                   fontcolor='black', style='filled')
            for h in self.heads:
                h.add_to_graph(s)
            self.ff_table.add_to_graph(s)

    def add_organising_edges(self, g):
        if self.ff_table.empty:
            return
        for h in self.heads:
            place_above(g, h, self.ff_table)

    def add_edges(self, g):
        for h in self.heads:
            h.add_edges(g)
        self.add_organising_edges(g)

    def layer_cluster_name(self, depth):
        return 'cluster_l'+str(depth)  # graphviz needs
        # cluster names to start with 'cluster'


class CompFlow:
    def __init__(self, all_heads, all_ffs, force_vertical_layers,
                 add_tokens_on_ff=False):
        self.force_vertical_layers = force_vertical_layers
        self.add_tokens_on_ff = add_tokens_on_ff
        self.make_all_layers(all_heads, all_ffs)

    def make_all_layers(self, all_heads, all_ffs):
        self.layers = []
        ff_depths = [seq.scheduled_comp_depth for seq in all_ffs]
        head_depths = [h.comp_depth for h in all_heads]
        depths = sorted(list(set(ff_depths+head_depths)))
        for d in depths:
            d_heads = [h for h in all_heads if h.comp_depth == d]
            d_heads = sorted(d_heads, key=lambda h: h.select.creation_order_id)
            # only important for determinism to help debug
            d_ffs = [f for f in all_ffs if f.scheduled_comp_depth == d]
            self.layers.append(Layer(d, d_heads, d_ffs, self.add_tokens_on_ff))

    def add_all_layers(self, g):
        [layer.add_to_graph(g) for layer in self.layers]

    def add_organising_edges(self, g):
        if self.force_vertical_layers:
            for l1, l2 in zip(self.layers, self.layers[1:]):
                place_above(g, l1, l2)

    def add_edges(self, g):
        self.add_organising_edges(g)
        [layer.add_edges(g) for layer in self.layers]


@UnfinishedFunc
def draw_comp_flow(self, w, filename=None,
                   keep_dot=False, show=True,
                   force_vertical_layers=True, add_tokens_on_ff=False):
    if w is not None:
        self(w)  # execute seq (and all its ancestors) on the given input w.
        # if w==None, assume seq has already been executed on some input.
        if not self.last_w == w:
            print("evaluating input failed")
            return
    else:
        w = self.last_w
    if None is filename:
        name = self.name
        filename = os.path.join("comp_flows", windows_path_cleaner(
            name+"("+(str(w) if not isinstance(w, str) else "\""+w+"\"")+")"))
    self.mark_all_minor_ancestors()
    self.make_display_names_for_all_parents(skip_minors=True)

    all_heads, all_ffs = self.get_all_ancestor_heads_and_ffs(
        remove_minors=True)
    # this scheduling also marks the analysis parent selects
    compflow = CompFlow(all_heads, all_ffs,
                        force_vertical_layers=force_vertical_layers,
                        add_tokens_on_ff=add_tokens_on_ff)

    # only import graphviz *inside* this function -
    # that way RASP can run even if graphviz setup fails
    # (though it will not be able to draw computation flows without it)
    from graphviz import Digraph
    g = Digraph('g')
    # with curved lines it fusses over separating score edges
    g.attr(splines='polyline')
    # and makes weirdly curved ones that start overlapping with the sequences
    # :(
    compflow.add_all_layers(g)
    compflow.add_edges(g)
    g.render(filename=filename)
    if show:
        g.view()
    if not keep_dot:
        os.remove(filename)

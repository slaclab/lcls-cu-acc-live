from lume_epics.client.controller import Controller
from lume_epics.client.widgets.tables import ValueTable
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc
from lume_model.utils import load_variables

prefix = "BMAD"
input_variables, output_variables = load_variables("model_variables.pickle")
controller = Controller("ca", input_variables, output_variables, prefix)


class TaoMonitor:

    def __init__(self, controller):
        self.controller = controller

        self.pvs = [
            "ele.name",
            "ele.ix_ele",
            "ele.ix_branch",
            "ele.a.beta",
            "ele.a.alpha",
            "ele.a.eta",
            "ele.a.etap",
            "ele.a.gamma",
            "ele.a.phi",
            "ele.b.beta",
            "ele.b.alpha",
            "ele.b.eta",
            "ele.b.etap",
            "ele.b.gamma",
            "ele.b.phi",
            "ele.x.eta",
            "ele.x.etap",
            "ele.y.eta",
            "ele.y.etap",
            "ele.s",
            "ele.l",
            "ele.e_tot",
            "ele.p0c",
            "ele.mat6",
            "ele.vec0"
        ]


    def poll(self):
        output =  {}

        for pv in self.pvs:
            val = self.controller.get_array(pv)
            output[pv] = val

        return output



monitor = TaoMonitor(controller)

p = figure(plot_width=800, plot_height=400)
p.xaxis.axis_label = 's (m)'
p.yaxis.axis_label = 'Twiss Beta (m)'

data = {'x':[0, 0, 0, 0],
   'y':[0,0,0,0]}
a_beta_cds = ColumnDataSource(data = data)
b_beta_cds = ColumnDataSource(data = data)

p.line(x="x", y="y", source=a_beta_cds, line_width=1, name = r'$\beta_a$')
p.line(x="x", y="y", source=b_beta_cds, line_width=1, name = r'$\beta_b$')


def plot_twiss():
    output = monitor.poll()

    if len(output["ele.a.beta"]) > 0:
        ele_s = output["ele.s"]
        ele_a_beta = output["ele.a.beta"]
        ele_b_beta = output["ele.b.beta"]

        a_beta_cds.data = {"x": ele_s, "y": ele_a_beta}
        b_beta_cds.data = {"x": ele_s, "y": ele_b_beta}


value_table = ValueTable(input_variables.values(), controller)

curdoc().add_root(column(p, value_table.table))
#curdoc().add_root(column(value_table.table))
#curdoc().add_root(column(p))
#for callback in callbacks:
curdoc().add_periodic_callback(plot_twiss, 1000)
curdoc().add_periodic_callback(value_table.update, 1000)







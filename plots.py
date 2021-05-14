from lume_epics.client.controller import Controller
from lume_epics.client.widgets.tables import ValueTable
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, HoverTool
from bokeh.io import curdoc
from lume_model.utils import load_variables

prefix = "DEMO"
input_variables, output_variables = load_variables("files/model_variables.pickle")
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


data = {'x':[0, 0, 0, 0],
   'y':[0,0,0,0], "name": [0,0,0,0]}

monitor = TaoMonitor(controller)

twiss = figure(plot_width=600, plot_height=200, tools="reset,pan,wheel_zoom,box_zoom")
twiss.xaxis.axis_label = 's (m)'
twiss.yaxis.axis_label = 'Twiss Beta (m)'

a_beta_cds = ColumnDataSource(data = data) # only want one hover tool
b_beta_cds = ColumnDataSource(data = data)

plota = twiss.line(x="x", y="y", source=a_beta_cds, line_width=1, name = r'$\beta_a$', legend_label="βx", line_color="red")
twiss.line(x="x", y="y", source=b_beta_cds, line_width=1, name = r'$\beta_b$', legend_label="βy")
twiss.legend.location = "top_left"
twiss.legend.label_text_font_size = '8pt'



# e total
e_total = figure(plot_width=600, plot_height=200, x_range=twiss.x_range, tools="reset,pan,wheel_zoom,box_zoom")
e_total.xaxis.axis_label = 's (m)'
e_total.yaxis.axis_label = 'Total Energy (GeV)'


e_tot_cds = ColumnDataSource(data = data)

e_total.line(x="x", y="y", source=e_tot_cds, line_width=1, name = r'$\e_tot$')

# a_eta b_etap
eta_etap = figure(plot_width=600, plot_height=200, x_range=twiss.x_range, tools="reset,pan,wheel_zoom,box_zoom")
eta_etap.xaxis.axis_label = 's (m)'
eta_etap.yaxis.axis_label = 'Dispersion (m)'


eta_cds = ColumnDataSource(data = data)
etap_cds = ColumnDataSource(data = data)

eta_etap_line = eta_etap.line(x="x", y="y", source=eta_cds, line_width=1, name = r'$\a_eta$', legend_label="ηx", line_color="black")
eta_etap.line(x="x", y="y", source=etap_cds, line_width=1, name = r'$\b_etap$', legend_label="ηy", line_color="green")
eta_etap.legend.label_text_font_size = '8pt'
eta_etap.legend.location = "bottom_left"


title_div = Div(text=f"<h1>LUME LCLS cu_hxr model</h1>", style={'color': 'blue', 'text-align': 'center'}, width=800)


output = monitor.poll()


hover_tool = HoverTool(
    tooltips=[
        ( 'name',   '@name'            ),
        ( 's',  '@{x}{0.2f}' ),
    ],

    formatters={
        'name'      : 'printf', # use 'datetime' formatter for 'date' field
        's': 'printf'
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
)


twiss_hovertool = HoverTool(
    tooltips=[
        ( 'name',   '@name'            ),
        ( 's',  '@{x}{0.2f}' ),
    ],

    formatters={
        'name'      : 'printf', # use 'datetime' formatter for 'date' field
        's': 'printf'
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline', 
    renderers= [plota]
)



eta_etap_hovertool = HoverTool(
    tooltips=[
        ( 'name',   '@name'            ),
        ( 's',  '@{x}{0.2f}' ),
    ],

    formatters={
        'name'      : 'printf', # use 'datetime' formatter for 'date' field
        's': 'printf'
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline', 
    renderers= [eta_etap_line]
)


twiss.add_tools(twiss_hovertool)
e_total.add_tools(hover_tool)
eta_etap.add_tools(eta_etap_hovertool)



def update_plots():
    output = monitor.poll()

    if len(output["ele.a.beta"]) > 0:
        ele_s = output["ele.s"]
        ele_name = output["ele.name"]

        #twiss
        ele_a_beta = output["ele.a.beta"]
        ele_b_beta = output["ele.b.beta"]

        a_beta_cds.data = {"x": ele_s, "y": ele_a_beta, "name": ele_name}
        b_beta_cds.data = {"x": ele_s, "y": ele_b_beta, "name": ele_name}

        # e_tot
        ele_e_tot = output["ele.e_tot"]
        ele_e_tot = ele_e_tot/1e9 # eV -> GeV
        e_tot_cds.data = {"x": ele_s, "y": ele_e_tot, "name": ele_name}

        # ele_a_eta & ele_b_etap
        ele_a_eta = output["ele.a.eta"]
        ele_b_etap = output["ele.b.etap"]
        eta_cds.data = {"x": ele_s, "y": ele_a_eta, "name": ele_name}
        etap_cds.data = {"x": ele_s, "y": ele_b_etap, "name": ele_name}



table_variables = [input_var for input_var in input_variables.values() if input_var.variable_type == "scalar"]
value_table = ValueTable(table_variables, controller)

curdoc().add_root(column(title_div, row(column(twiss, e_total, eta_etap), value_table.table), sizing_mode="scale_width"))
#curdoc().add_root(column(value_table.table))
#curdoc().add_root(column(p))
#for callback in callbacks:
curdoc().add_periodic_callback(update_plots, 500)
curdoc().add_periodic_callback(value_table.update, 500)







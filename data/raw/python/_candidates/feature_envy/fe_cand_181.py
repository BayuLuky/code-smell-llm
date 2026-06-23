def __init__(self, root, controller):
    f = Figure()
    ax = f.add_subplot(111)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim((x_min, x_max))
    ax.set_ylim((y_min, y_max))
    canvas = FigureCanvasTkAgg(f, master=root)
    try:
        canvas.draw()
    except AttributeError:
        # support for matplotlib (1.*)
        canvas.show()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas.mpl_connect("button_press_event", self.onclick)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    self.controllbar = ControllBar(root, controller)
    self.f = f
    self.ax = ax
    self.canvas = canvas
    self.controller = controller
    self.contours = []
    self.c_labels = None
    self.plot_kernels()

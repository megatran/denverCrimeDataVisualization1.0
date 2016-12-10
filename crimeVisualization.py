import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import font
import pg8000

LARGE_FONT = ("Verdana", 12)

def pull_data(db, string_query, *args, **kwargs):
    ###############
    # pass in login windows
    db = db
    cursor = db.cursor()
    query = string_query
    query_additional = kwargs.get('query_additional', None)
    # print(query_additional)
    # print(type(query_additional))
    if query_additional is not None and type(query_additional) is not tuple:
        raise ValueError("Error in Query. Additional query must be type tuple")
    try:
        if query_additional is not None and len(query_additional) > 0:
            #print(query_additional)
            cursor.execute(query, query_additional)
        else:
            cursor.execute(query)

        resultset = cursor.fetchall()

        return resultset
    except pg8000.Error as e:
        messagebox.showerror('Database error', e.args[2])
        return None

    ##############

class SeaofBTCapp(tk.Tk):
    def __init__(self, db,*args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #tk.Tk.iconbitmap(self, default="icon.ico")
        tk.Tk.wm_title(self, "Crime Data Visualization")

        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()



class StartPage(tk.Frame):

    # Variables
    offenseTypeFilter = ''
    neighborhoods = []
    neighTicks = []
    crimes = []

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = ttk.Button(self, text="Crimes Per Month",
                           command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()

        self.loadData()
        self.loadButtons()
    
    def loadButtons(self):
        # SQL
        # Offense types
        offenseTypes = []
        offenseQuery = """SELECT DISTINCT offense_type_id FROM denver_crime ORDER BY offense_type_id"""
        resultSet = pull_data(lwapp.db, offenseQuery)
        for r in resultSet:
            offenseTypes.append(r[0])

        # Buttons and more
        mainlabel = tk.Label(self, text="Filter By: ", font=LARGE_FONT)
        mainlabel.pack()

        crimeTypeFilter = Combobox(self, values = offenseTypes, text='Incident Type')
        crimeTypeFilter.bind("<<ComboboxSelected>>")
        crimeTypeFilter.pack()
        liveF = Figure(figsize=(10,4), dpi=100)
        a = liveF.add_subplot(111)
        go = ttk.Button(self, text="Apply",
                            command=lambda: self.updateGraph(crimeTypeFilter, a ,canvas))
        go.pack()




        a.set_xticks(self.neighTicks)
        a.set_xticklabels(self.neighborhoods)
        liveF.autofmt_xdate()
        matplotlib.rcParams.update({'font.size': 7})

        canvas = FigureCanvasTkAgg(liveF, self)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)

        self.updateGraph(crimeTypeFilter, a, canvas)



    def loadData(self):
        # Query Info
        mainQuery = """SELECT neighborhood_id, count(neighborhood_id) FROM denver_crime WHERE offense_type_id LIKE (%s)
                GROUP BY neighborhood_id ORDER BY count(neighborhood_id) DESC"""

        if self.offenseTypeFilter == '':
            self.offenseTypeFilter = '%'

        newPrep = '%' + self.offenseTypeFilter + '%'
        prepared = (newPrep,)
        resultSet = pull_data(lwapp.db, mainQuery, query_additional=prepared)



        print()
        self.neighborhoods[:] = []
        self.crimes[:] = []
        for r in resultSet:
            self.neighborhoods.append(r[0])
            self.crimes.append(r[1])

        self.neighTicks[:] = []
        i = 1
        for x in self.neighborhoods:
            self.neighTicks.append(i)
            i += 1


    def updateGraph(self, box, a, c):

        self.offenseTypeFilter = box.get()
        self.loadData()
        a.clear()
        print("UPDATE GRAPH")
        print(self.crimes)
        a.bar(self.neighTicks, self.crimes, width=1)
        c.show()

        




class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Crimes per Month", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        query = """SELECT count(*) FROM denver_crime WHERE reported_date::text LIKE (%s) AND is_crime;"""

        resultMonthTick = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        resultMonth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        resultCrime = []

        for x in range(1, 10):
            prepared = ('%-' + '0' + str(x) + '-%',)
            resultCrime.append(pull_data(lwapp.db, query, query_additional = prepared)[0][0])

        for x in range(10, 13):
            prepared = ('%-' + str(x) + '-%',)
            resultCrime.append(pull_data(lwapp.db, query, query_additional = prepared)[0][0])
        
        # print(resultCrime)

        cpm = Figure(figsize=(5,5), dpi=100)
        a = cpm.add_subplot(111) #111 means 1 by 1, 121 means 1 by 2

        a.set_xticks(resultMonthTick)
        a.set_xticklabels(resultMonth)
        a.plot(resultMonthTick, resultCrime)

        canvas = FigureCanvasTkAgg(cpm, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Pie Chart", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()
    # All you need to change in here are to take the two count results from the query and put them in the proper place, and take the plot and put it on the canvas. If you run the file as is, you'll see what the pie chart would look like, just not in the actual application.

    # Here are the queries that give you the results for what you need. Replace 215 and 130 in the
    # sizes = [215,130] line with the results accordingly

        other_query = """SELECT count(*) FROM denver_crime WHERE is_crime"""
        traffic_query = """SELECT count(*) FROM denver_crime WHERE is_traffic"""
        both_query = """SELECT count(*) FROM denver_crime WHERE is_crime AND is_traffic"""

        non_traffic_count = pull_data(lwapp.db, other_query)
        traffic_count = pull_data(lwapp.db, traffic_query)
        both_count = pull_data(lwapp.db, both_query)

        print("TRAFFIC COUNT IS")
        print(traffic_count, non_traffic_count, both_count)
        # Data to plot


        labels = ['Traffic-Related', 'Non-traffic crime', 'Both' ]

        # Get these from the query
        sizes = [traffic_count[0], non_traffic_count[0], both_count[0]]
        colors = ['red', 'green', 'gold']
        explode = (0.1, 0, 0)  # explode 1st slice

        # Plot
        f = Figure(figsize=(5, 5), dpi=100)
        plt = f.add_subplot(111)
        plt.legend(title="Percentage of Incidents (Crime, Traffic, Both)")
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')


        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # add navigation bar
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack()

        # import matplotlib
    	# matplotlib.use("TkAgg")

    	# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
    	# from matplotlib.figure import Figure
    	# import matplotlib.pyplot as plt

    	# #All you need to change in here are to take the two count results from the query and put them in the proper place, and take the plot and put it on the canvas. If you run the file as is, you'll see what the pie chart would look like, just not in the actual application.

    	# #Here are the queries that give you the results for what you need. Replace 215 and 130 in the
    	# #sizes = [215,130] line with the results accordingly
    	# otherquery = """"""SELECT count(*) FROM denver_crime WHERE NOT is_traffic;"""
    	# """trafficquery = """"""SELECT count(*) FROM denver_crime WHERE is_traffic;"""

    	# # Data to plot
    	# """labels = 'Traffic-Related', 'All other Incidents'

    	# #Get these from the query
    	# sizes = [215, 130]
    	# colors = ['red', 'green']
    	# explode = (0.1, 0)  # explode 1st slice
    		 
    	# # Plot
    	# plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    		 
    	# plt.axis('equal')
    	# plt.show()

        

class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        ###database setup###
        ###configure db####
        query = """SELECT precinct_id, count(precinct_id) FROM denver_crime GROUP BY precinct_id ORDER BY count(precinct_id) DESC"""
        result = pull_data(lwapp.db, query)
        #print(result)

        #draw things in backend then bring to front (matplotlib)

        f = Figure(figsize=(5,5), dpi=100)
        plt = f.add_subplot(111) #111 means 1 by 1, 121 means 1 by 2
        #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        #a.plot(result[0], result[1])

        x_chart, y_chart = [],[]
        for res in result:
            # print(res[0], res[1])
            if res[0] is not None and res[1] is not None:
                x_chart.append(res[0])
                y_chart.append(res[1])

        #print(x_chart)
        #print(y_chart)

       # width = 1/1.5
        x = range(len(x_chart))
        plt.bar(x,y_chart, align="center", color="blue")
        plt.set_xticks(x)
        plt.set_xticklabels(x_chart)
        plt.set_xlabel("Precints")
        plt.set_ylabel("Crime Count")
        plt.set_title("Crimes by Precints")
        #plt.autoscale_view(True, True, True)

        f.autofmt_xdate()
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)

        #add navigation bar
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack()

# implements a simple login window
class LoginWindow:
    def __init__(self, window):
        self.window = window

        self.window.title('Login')
        self.window.grid()

        # styling
        self.font = font.Font(family='Arial', size=12)
        Style().configure('TButton', font=self.font)
        Style().configure('TLabel', font=self.font)

        # setup widgets
        self.user_label = Label(window, text='Username: ')
        self.user_label.grid(column=0, row=0)
        self.user_input = Entry(window, width=20, font=self.font)
        self.user_input.grid(column=1, row=0)

        self.pw_label = Label(window, text='Password: ')
        self.pw_label.grid(column=0, row=1)
        self.pw_input = Entry(window, width=20, show='*', font=self.font)
        self.pw_input.grid(column=1, row=1)

        self.button_frame = Frame(window)
        self.button_frame.grid(column=0, columnspan=2, row=2)

        self.ok_button = Button(self.button_frame, text='OK', command=self.ok_action)
        self.ok_button.grid(column=0, row=0)

        self.cancel_button = Button(self.button_frame, text='Cancel', command=quit)
        self.cancel_button.grid(column=1, row=0)

        self.window.bind('<Return>', self.enter_action)
        self.user_input.focus_set()

    def enter_action(self, event):
        self.ok_action()

    def ok_action(self):
        try:
            credentials = {'user': self.user_input.get(),
                           'password': self.pw_input.get(),
                           'database': 'csci403',
                           'host': 'flowers.mines.edu'}
            self.db = pg8000.connect(**credentials)
            self.window.destroy()
        except pg8000.Error as e:
            messagebox.showerror('Login Failed', e.args[2])
            # end LoginWindow



#main program
lw = tk.Tk()
lwapp = LoginWindow(lw)
lw.mainloop()
app = SeaofBTCapp(lwapp.db)
app.mainloop()

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

def pull_data(db, string_query):
    ###############
    # pass in login windows
    db = db
    cursor = db.cursor()
    query = string_query
    try:
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

        ###configure db####
        query = """SELECT precinct_id, count(precinct_id) FROM denver_crime GROUP BY precinct_id ORDER BY count(precinct_id) DESC"""
        result = pull_data(db, query)
        print(result)
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
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = ttk.Button(self, text="Visit Page 1",
                           command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Crimes per Month", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        query = """SELECT count(*) FROM denver_crime WHERE reported_date::text LIKE '%-(%s)-%' AND is_crime;"""

        resultMonth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        resultCrime = []

        for x in range(1, 13)
            resultCrime.append(pull_data(self, query))

        

        cpm = Figure(figsize=(5,5), dpi=100)
        a = cpm.add_subplot(111) #111 means 1 by 1, 121 means 1 by 2

        a.plot(resultMonth, resultCrime)



        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()




class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page One",
                            command=lambda: controller.show_frame(PageOne))
        button2.pack()

class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        #draw things in backend then bring to front (matplotlib)

        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111) #111 means 1 by 1, 121 means 1 by 2
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

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
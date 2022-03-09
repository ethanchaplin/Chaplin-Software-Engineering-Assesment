from tkinter import *
from tkinter import messagebox
from secrets import randbelow
import numpy as np


class Grid:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.grid = np.zeros(shape=(self.rows, self.columns))

    # Interpolates data at given point in the grid using values from neighbors

    def interpolate(self, row, col):
        # Keeps rolling sum of neighbors as it loops through each one
        rolling_sum = 0
        # Keeps track of how many neighbors that have been interacted with
        counter = 0
        try:
            self.grid[row][col]
        except:
            messagebox.showerror(
                "Interpolation Error", "Please enter only numbers into the grid!"
            )

        else:
            # Loop through all possible neighbor combinations (-1, -1), (-1, 0), ...
            for i in range(-1, 2):
                for j in range(-1, 2):

                    # Ignores currently selected cell
                    if not (i == 0 and j == 0):
                        # Checks if cell being reached is valid. If not, it is ignored.
                        if (
                            (row + i < 0)
                            or (col + j < 0)
                            or (row + i == self.rows)
                            or (col + j == self.columns)
                        ):
                            counter += 0
                        else:
                            rolling_sum += self.grid[row + i][col + j]
                            counter += 1
            # Sets point at grid to the average of the cells neighbors
            self.grid[row][col] = rolling_sum / counter

    # Updates internal matrix for given grid at point (row, col)
    # Safer than explicitly using 'grid[row][col]', as function contains error checking
    def updateGrid(self, row, col, val):
        try:
            self.grid[row][col] = val
        except:
            messagebox.showerror(
                "Interpolation Error", "That is not a valid cell location!"
            )

    def getVal(self, row, column):
        return self.grid[row, column]


class UI:
    def __init__(self, WIDTH, HEIGHT, SENSOR_ROWS, SENSOR_COLUMNS):

        # Set number of sensors per row/column, default values
        # Can be reconfigured later
        self.SENSOR_ROWS = SENSOR_ROWS
        self.SENSOR_COLUMNS = SENSOR_COLUMNS

        # Set default window height
        self.WINDOW_HEIGHT = HEIGHT
        self.WINDOW_WIDTH = WIDTH

        # Establish default canvas size is 1/4 the size of the window
        self.CAN_HEIGHT = self.WINDOW_HEIGHT / 2
        self.CAN_WIDTH = self.WINDOW_WIDTH / 2

        # Keeps track if grid values displayed are rounded or full decimal
        self.rounded = False

        self.grid = Grid(self.SENSOR_ROWS, self.SENSOR_COLUMNS)

        # Initialize tkinter window
        self.root = Tk()
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.title("Chaplin Software Engineering Co-op Technical Assessment")
        # Create northwest quadrant (contains grid)
        self.canvas = Canvas(self.root, height=self.CAN_HEIGHT, width=self.CAN_WIDTH)
        self.canvas.pack()
        self.canvas.place(relx=0.0, rely=0.0, anchor=NW)

        # Create southwest quadrant (contains decimal/integer button)
        self.canvas_sw = Canvas(self.root, height=self.CAN_HEIGHT, width=self.CAN_WIDTH)
        self.canvas_sw.pack()
        self.canvas_sw.place(relx=0.0, rely=1.0, anchor=SW)

        # Create northeast quadrant (contains interpolate button and cell selector)
        self.canvas_ne = Canvas(self.root, height=self.CAN_HEIGHT, width=self.CAN_WIDTH)
        self.canvas_ne.pack()
        self.canvas_ne.place(relx=1.0, rely=0.0, anchor=NE)

        # Create menubar
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.fileMenu = Menu(self.menubar)

        self.menubar.add_cascade(label="Grid", menu=self.fileMenu)
        self.fileMenu.add_command(label="Fill Random", command=self.fillRandom)
        self.fileMenu.add_command(label="Fill Zeros", command=self.fillZeros)

        # General GUI initialization

        self.INTERPOLATE_Y = self.WINDOW_HEIGHT / 4

        self.b2 = Button(
            self.canvas_ne, text="Interpolate Cell", command=self.interpolateAndUpdate
        )
        self.canvas_ne.create_window(200, self.INTERPOLATE_Y, window=self.b2)

        self.cell_help_left = Label(self.canvas_ne, text="(")
        self.cell_help_middle = Label(self.canvas_ne, text=",")
        self.cell_help_right = Label(self.canvas_ne, text=")")

        self.cell_help_row = Label(self.canvas_ne, text="row")
        self.cell_help_column = Label(self.canvas_ne, text="column")

        self.e2 = Entry(self.canvas_ne, width=5)
        self.e2.insert(0, "0")

        self.e3 = Entry(self.canvas_ne, width=5)
        self.e3.insert(0, "0")

        self.canvas_ne.create_window(300, self.INTERPOLATE_Y, window=self.e2)
        self.canvas_ne.create_window(350, self.INTERPOLATE_Y, window=self.e3)

        self.canvas_ne.create_window(
            275, self.INTERPOLATE_Y, window=self.cell_help_left
        )
        self.canvas_ne.create_window(
            325, self.INTERPOLATE_Y, window=self.cell_help_middle
        )
        self.canvas_ne.create_window(
            375, self.INTERPOLATE_Y, window=self.cell_help_right
        )

        self.canvas_ne.create_window(
            298, self.INTERPOLATE_Y + 25, window=self.cell_help_row
        )
        self.canvas_ne.create_window(
            348, self.INTERPOLATE_Y + 25, window=self.cell_help_column
        )

        # Disable resizing for now, things can get ugly without proper scaling
        # Would implement automatic scaler but that's out of the scope of this project
        self.root.resizable(False, False)

        # Refresh elements once before initial boot
        self.populateEntries()
        # Begin tkinter loop
        self.root.mainloop()

    def populateEntries(self):

        # Clears canvas for repainted values
        self.canvas.delete("all")
        self.canvas_sw.delete("all")

        # Redraws every Entry widget with updated values according to the given matrix
        for i in range(self.SENSOR_ROWS):
            for j in range(self.SENSOR_COLUMNS):
                # Each entry is given a unique name with its individual position, so that
                # it can be referenced later
                e1 = Entry(self.canvas, width=6, name=f"{i}:{j}")

                self.canvas.create_window(
                    (self.CAN_WIDTH / self.SENSOR_ROWS) * i + 45,
                    (self.CAN_HEIGHT / self.SENSOR_COLUMNS) * j + 30,
                    window=e1,
                )
                if self.rounded:
                    e1.insert(0, str(int(round(self.grid.getVal(i, j)))))
                else:

                    e1.insert(0, str(self.grid.getVal(i, j)))

                # Binds a keyrelease event to each Entry widget, so that it automatically updates
                # whenever the keyboard is used while using the text box.
                e1.bind("<KeyRelease>", self.updateEntry)

        # Indicator labels that show rows/columns
        l1 = Label(self.canvas, text="0")
        l4 = Label(self.canvas, text="0")
        l2 = Label(self.canvas, text=str(self.SENSOR_COLUMNS - 1))
        l3 = Label(self.canvas, text=str(self.SENSOR_ROWS - 1))

        # Draw 0s
        self.canvas.create_window(10, 30, window=l1)
        self.canvas.create_window(45, 10, window=l4)

        # Draw row/column indicators exactly in line with Entry widgets. Scales to more or less columns/rows
        self.canvas.create_window(
            (self.CAN_WIDTH / self.SENSOR_ROWS) * (self.SENSOR_ROWS - 1) + 45,
            10,
            window=l3,
        )
        self.canvas.create_window(
            10,
            (self.CAN_HEIGHT / self.SENSOR_COLUMNS) * (self.SENSOR_COLUMNS - 1) + 30,
            window=l2,
        )

        # Toggle name of button based on the state of 'rounded'
        if self.rounded:
            b1 = Button(
                self.canvas_sw, text="Show True Values", command=self.toggleRound
            )
        else:
            b1 = Button(
                self.canvas_sw, text="Show Rounded Values", command=self.toggleRound
            )

        # Draw toggle button
        self.canvas_sw.create_window(self.WINDOW_WIDTH / 4, 50, window=b1)
        self.canvas_sw.pack()
        self.canvas_sw.place(relx=0.0, rely=1.0, anchor=SW)

        self.canvas.pack()
        self.canvas.place(relx=0.0, rely=0.0, anchor=NW)

    # Entry event detector
    # Removes accidental letters and symbols typed so that only numbers are entered
    def updateEntry(self, event):

        illegal = "!@#$%^&*()_-+={}[]"

        # Unique name from Entry widget that called update function is used to update
        # value at correct position in the grid
        pos = str(event.widget)[-3:].split(":")

        # If the character typed is a number, perform normally.
        if event.keysym.isnumeric():

            self.grid.updateGrid(int(pos[0]), int(pos[1]), float(event.widget.get()))

        # Check if keyboard event contains one letter, because events like 'Return' wil be
        # flagged if not
        elif len(event.keysym) == 1 and (
            (event.keysym.isalpha()) or (event.keysym in illegal)
        ):
            # Get value of Entry widget before the letter was typed
            txt = event.widget.get()[:-1]

            # Delete and refresh value without letter
            event.widget.delete(0, END)
            event.widget.insert(0, txt)

        # If enter is pressed, automatically interpolate the cell which is selected
        elif event.keysym == "Return":
            self.grid.interpolate(int(pos[0]), int(pos[1]))
            self.populateEntries()

    # Toggles rounded variable whenever called
    def toggleRound(self):

        self.rounded = not self.rounded
        self.populateEntries()

    # Fills grid with random integers 0-100
    def fillRandom(self):
        for x in range(self.SENSOR_ROWS):
            for y in range(self.SENSOR_COLUMNS):
                self.grid.updateGrid(x, y, randbelow(100))
        self.populateEntries()

    # Fills grid with zeros
    def fillZeros(self):
        for x in range(self.SENSOR_ROWS):
            for y in range(self.SENSOR_COLUMNS):
                self.grid.updateGrid(x, y, 0)
        self.populateEntries()

    # Combo function of interpolation() and populateEntries()
    # For use as a button call
    def interpolateAndUpdate(self):

        try:
            self.grid.interpolate(int(self.e3.get()), int(self.e2.get()))
        except:
            messagebox.showerror(
                "Interpolation Error", "Please enter a valid cell location!"
            )
        else:
            self.populateEntries()

if(__name__=="__main__"):   
    # Initialize main window
    main_ui = UI(960, 540, 6, 6)
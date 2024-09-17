#!/usr/bin/env python3

import sys
import argparse
from tkinter import *
from tkinter import simpledialog
from PIL import Image, ImageTk

class ImageBoxDrawer:
	def __init__(self, root, image_path, pan_sensitivity):
		self.root = root
		self.root.title("Image Box Drawer")
		self.image_path = image_path
		self.image = Image.open(image_path)
		self.orig_width, self.orig_height = self.image.size

		# Initialize scale factor and zoom
		self.scale_factor = 1.0
		self.zoom_factor = 1.0
		self.pan_sensitivity = pan_sensitivity  # Sensitivity for panning

		# Canvas to display the image
		self.canvas = Canvas(root, bg='white')
		self.canvas.pack(fill=BOTH, expand=YES)

		# Load and display the image
		self.load_image()

		# Bind events for resizing, mouse wheel, and keyboard zoom
		self.root.bind('<Configure>', self.on_resize)
		self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
		self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux support for mouse wheel
		self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux support for mouse wheel
		self.root.bind("+", self.on_zoom_in)
		self.root.bind("-", self.on_zoom_out)

		# Bind mouse events for drawing and panning
		self.canvas.bind("<ButtonPress-1>", self.on_button_press)
		self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
		self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
		self.canvas.bind("<ButtonPress-3>", self.on_right_click_press)  # Right-click press for panning
		self.canvas.bind("<B3-Motion>", self.on_right_click_drag)        # Right-click drag for panning

		# Rectangle tracking variables
		self.rect = None
		self.start_x = None
		self.start_y = None

		# Variables for panning
		self.pan_start_x = None
		self.pan_start_y = None
		self.canvas_start_x = 0
		self.canvas_start_y = 0

	def load_image(self):
		# Rescale the image according to zoom factor
		new_width = int(self.orig_width * self.zoom_factor)
		new_height = int(self.orig_height * self.zoom_factor)
		self.image_resized = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
		self.tk_image = ImageTk.PhotoImage(self.image_resized)

		# Clear the canvas and redraw the image
		self.canvas.delete("all")
		self.canvas.create_image(0, 0, anchor=NW, image=self.tk_image)
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

	def on_resize(self, event):
		# Adjust the image to fit the window when resized
		window_width = event.width
		window_height = event.height

		# Calculate the best scale factor to fit the image within the resized window
		self.zoom_factor = min(window_width / self.orig_width, window_height / self.orig_height)

		# Load the resized image
		self.load_image()

	def on_mouse_wheel(self, event):
		# Zoom in or out using the mouse wheel
		if event.delta > 0 or event.num == 4:  # Scroll up
			self.zoom_in()
		elif event.delta < 0 or event.num == 5:  # Scroll down
			self.zoom_out()

	def on_zoom_in(self, event=None):
		self.zoom_in()

	def on_zoom_out(self, event=None):
		self.zoom_out()

	def zoom_in(self):
		# Increase the zoom factor and reload the image
		self.zoom_factor *= 1.1
		self.load_image()

	def zoom_out(self):
		# Decrease the zoom factor and reload the image
		self.zoom_factor *= 0.9
		self.load_image()

	def on_button_press(self, event):
		# Record the starting coordinates for the rectangle
		self.start_x = self.canvas.canvasx(event.x)
		self.start_y = self.canvas.canvasy(event.y)

		# Create a new rectangle
		self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

	def on_mouse_drag(self, event):
		# Update the size of the rectangle as the mouse is dragged
		cur_x = self.canvas.canvasx(event.x)
		cur_y = self.canvas.canvasy(event.y)
		self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

	def on_button_release(self, event):
		# Record the ending coordinates for the rectangle
		end_x = self.canvas.canvasx(event.x)
		end_y = self.canvas.canvasy(event.y)

		# Convert the coordinates to the original image dimensions
		start_x_orig = int(self.start_x / self.zoom_factor)
		start_y_orig = int(self.start_y / self.zoom_factor)
		end_x_orig = int(end_x / self.zoom_factor)
		end_y_orig = int(end_y / self.zoom_factor)

		# Popup to get the name for the box and remove the rectangle
		box_name = simpledialog.askstring("Input", "Enter box name:", parent=self.root)
		self.canvas.delete(self.rect)

		if box_name:
			# Output the box name and coordinates
			print(f"{box_name}: {start_x_orig},{start_y_orig} {end_x_orig},{end_y_orig}")

		# Remove the rectangle regardless of the input
		self.rect = None

	def on_right_click_press(self, event):
		# Store the start of the right-click press for panning
		self.pan_start_x = event.x
		self.pan_start_y = event.y
		self.canvas_start_x = self.canvas.canvasx(0)
		self.canvas_start_y = self.canvas.canvasy(0)

	def on_right_click_drag(self, event):
		# Pan the image based on the mouse drag distance, with sensitivity applied
		dx = (self.pan_start_x - event.x) / (self.orig_width * self.zoom_factor)
		dy = (self.pan_start_y - event.y) / (self.orig_height * self.zoom_factor)

		# Move the canvas using xview_moveto and yview_moveto for smooth panning
		self.canvas.xview_moveto((self.canvas_start_x / self.orig_width) + dx / self.pan_sensitivity)
		self.canvas.yview_moveto((self.canvas_start_y / self.orig_height) + dy / self.pan_sensitivity)

def main():
	parser = argparse.ArgumentParser(description="Image Box Drawer with Resizing, Zoom, and Panning")
	parser.add_argument('--image', required=True, help="Path to the image file")
	parser.add_argument('--pan-sensitivity', type=float, default=1.0, help="Sensitivity for panning (default=1.0)")
	args = parser.parse_args()

	# Set up the Tkinter GUI
	root = Tk()
	app = ImageBoxDrawer(root, args.image, args.pan_sensitivity)
	root.mainloop()

if __name__ == "__main__":
	main()


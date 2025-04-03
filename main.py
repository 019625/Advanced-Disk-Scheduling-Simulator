import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from algorithms import fcfs, sstf, scan, cscan, look, clook
import matplotlib.animation as animation
import time

class DiskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Simulator")
        self.root.geometry("1400x900")

        # Variables
        self.requests = []
        self.head_position = tk.IntVar(value=50)
        self.disk_size = tk.IntVar(value=200)
        self.algorithm = tk.StringVar(value="FCFS")
        self.animation_speed = tk.IntVar(value=500)
        self.is_animating = False
        self.anim = None

        # Configure grid weights for centering
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Left panel for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="nsew")

        # Input fields
        ttk.Label(control_frame, text="Head Position:", font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)
        ttk.Entry(control_frame, textvariable=self.head_position).grid(row=0, column=1, pady=5)

        ttk.Label(control_frame, text="Disk Size:", font=('Arial', 10, 'bold')).grid(row=1, column=0, pady=5)
        ttk.Entry(control_frame, textvariable=self.disk_size).grid(row=1, column=1, pady=5)

        ttk.Label(control_frame, text="Request Queue:", font=('Arial', 10, 'bold')).grid(row=2, column=0, pady=5)
        self.request_entry = ttk.Entry(control_frame, width=30)
        self.request_entry.grid(row=2, column=1, pady=5)
        self.request_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")

        # Animation speed slider
        ttk.Label(control_frame, text="Animation Speed:", font=('Arial', 10, 'bold')).grid(row=3, column=0, pady=5)
        speed_slider = ttk.Scale(control_frame, from_=100, to=1000, 
                               variable=self.animation_speed, 
                               orient='horizontal')
        speed_slider.grid(row=3, column=1, pady=5, sticky="ew")

        # Algorithm selection
        algorithms = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
        ttk.Label(control_frame, text="Algorithm:", font=('Arial', 10, 'bold')).grid(row=4, column=0, pady=5)
        algorithm_menu = ttk.Combobox(control_frame, textvariable=self.algorithm, values=algorithms)
        algorithm_menu.grid(row=4, column=1, pady=5)

        # Buttons with styled appearance
        style = ttk.Style()
        style.configure('Custom.TButton', padding=5, font=('Arial', 10, 'bold'))
        
        ttk.Button(control_frame, text="Simulate", command=self.simulate, style='Custom.TButton').grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(control_frame, text="Clear", command=self.clear, style='Custom.TButton').grid(row=6, column=0, columnspan=2, pady=5)

        # Right panel for visualization - bigger plot
        self.setup_plot()

    def setup_plot(self):
        try:
            # Clean up any existing animation
            self.stop_animation()
            
            # Clean up any existing canvas
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            
            # Clean up any existing figure
            if hasattr(self, 'fig'):
                plt.close(self.fig)
            
            self.fig, self.ax = plt.subplots(figsize=(12, 8))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
            self.canvas.get_tk_widget().grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        except Exception as e:
            print(f"Error in setup_plot: {e}")

    def stop_animation(self):
        try:
            if self.anim is not None and hasattr(self.anim, 'event_source') and self.anim.event_source is not None:
                self.anim.event_source.stop()
                self.is_animating = False
                self.anim = None
        except Exception as e:
            print(f"Error stopping animation: {e}")

    def animate(self, frame):
        try:
            if frame >= len(self.sequence):
                self.stop_animation()
                return

            # Clear the previous frame
            self.ax.clear()

            # Get the current sequence up to the current frame
            current_sequence = self.sequence[:frame + 1]
            x = list(range(len(current_sequence)))
            y = current_sequence

            # Plot with animation
            color1, color2 = self.color_map[self.algorithm.get()]
            
            # Plot lines up to current point
            if len(x) > 1:
                self.ax.plot(x[:-1], y[:-1], '-', color=color1, linewidth=2.5, zorder=1)
            
            # Plot all previous points
            if len(x) > 1:
                self.ax.scatter(x[:-1], y[:-1], c=color1, s=100, zorder=2, edgecolor=color2, linewidth=2)
            
            # Highlight current point with different color
            if len(x) > 0:
                self.ax.scatter(x[-1], y[-1], c='red', s=150, zorder=3, edgecolor='white', linewidth=2)

            # Customize appearance
            self.ax.set_xlabel("Request Sequence", fontsize=12, fontweight='bold')
            self.ax.set_ylabel("Disk Position", fontsize=12, fontweight='bold')
            self.ax.set_title(f"{self.algorithm.get()} Disk Scheduling", fontsize=14, fontweight='bold', pad=20)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.set_facecolor('#f8f9fa')

            # Set y-axis limits based on disk size
            self.ax.set_ylim(-10, self.disk_size.get() + 10)

            # Show current head movement
            if frame > 0:
                current_movement = sum(abs(self.sequence[i] - self.sequence[i-1]) for i in range(1, frame + 1))
                self.ax.text(0.02, 0.98, f'Current head movement: {current_movement}', 
                            transform=self.ax.transAxes, 
                            verticalalignment='top',
                            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                            fontsize=11,
                            fontweight='bold')

            plt.tight_layout()
        except Exception as e:
            print(f"Error in animate: {e}")
            self.stop_animation()

    def simulate(self):
        try:
            # Stop any existing animation and reset plot
            self.stop_animation()
            self.setup_plot()

            # Get input values
            request_queue = [int(x.strip()) for x in self.request_entry.get().split(",")]
            head_pos = self.head_position.get()
            disk_size = self.disk_size.get()

            # Color scheme for different algorithms
            self.color_map = {
                "FCFS": ('#FF6B6B', '#4ECDC4'),    # Red to Turquoise
                "SSTF": ('#A8E6CF', '#FF8B94'),    # Mint to Pink
                "SCAN": ('#6C5B7B', '#C06C84'),    # Purple to Rose
                "C-SCAN": ('#45B7D1', '#FFBE0B'),  # Blue to Yellow
                "LOOK": ('#96CEB4', '#FFEEAD'),    # Sage to Cream
                "C-LOOK": ('#9B5DE5', '#00BBF9')   # Purple to Sky Blue
            }

            # Run selected algorithm
            algorithm_map = {
                "FCFS": fcfs,
                "SSTF": sstf,
                "SCAN": scan,
                "C-SCAN": cscan,
                "LOOK": look,
                "C-LOOK": clook
            }

            self.sequence = algorithm_map[self.algorithm.get()](request_queue, head_pos, disk_size)
            
            # Create new animation
            self.is_animating = True
            self.anim = animation.FuncAnimation(
                self.fig, 
                self.animate, 
                frames=len(self.sequence),
                interval=self.animation_speed.get(),
                repeat=False
            )
            
            self.canvas.draw()
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear(self):
        try:
            self.stop_animation()
            self.setup_plot()
            self.request_entry.delete(0, tk.END)
            self.request_entry.insert(0, "98, 183, 37, 122, 14, 124, 65, 67")
            self.head_position.set(50)
            self.canvas.draw()
        except Exception as e:
            print(f"Error in clear: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulerApp(root)
    root.mainloop() 
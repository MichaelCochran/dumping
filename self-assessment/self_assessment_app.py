import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import math


class SelfAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Development Self-Assessment")
        self.root.geometry("1200x800")
        
        self.categories = [
            "Technical Skills",
            "Interpersonal Skills",
            "Communication",
            "Learning Ability",
            "Leadership",
            # "Financial Skills",  # Uncomment if business/budget management is relevant
            "Problem Solving",
            "Learning Habits & Development",
            "Emotional Intelligence",
            "Systems Thinking",
            "Adaptability",
            "Time Management",
            "Creativity",
            "Collaboration",
            "Attention to Detail",
            "Self-Motivation",
            "Decision Making",
            "Cultural Awareness",
            "Influence & Persuasion"
        ]
        
        self.scores = {}
        self.current_category_index = 0
        self.chart_figure = None
        self.canvas_widget = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.question_frame = ttk.Frame(main_frame)
        self.question_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.chart_frame = ttk.Frame(main_frame)
        self.chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.show_question_interface()
    
    def show_question_interface(self):
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        if self.current_category_index < len(self.categories):
            category = self.categories[self.current_category_index]
            
            progress_text = f"Question {self.current_category_index + 1} of {len(self.categories)}"
            ttk.Label(self.question_frame, text=progress_text, font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
            
            ttk.Label(self.question_frame, text=f"Rate your ability in:", font=('Arial', 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
            ttk.Label(self.question_frame, text=category, font=('Arial', 16, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=10)
            
            ttk.Label(self.question_frame, text="(1 = Needs Significant Improvement, 10 = Exceptional)", font=('Arial', 10, 'italic')).grid(row=3, column=0, sticky=tk.W, pady=5)
            
            scale_frame = ttk.Frame(self.question_frame)
            scale_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=20)
            
            self.score_var = tk.IntVar(value=5)
            self.score_label = ttk.Label(scale_frame, text="5", font=('Arial', 24, 'bold'))
            self.score_label.grid(row=0, column=0, pady=10)
            
            scale = ttk.Scale(scale_frame, from_=1, to=10, orient=tk.HORIZONTAL, 
                            variable=self.score_var, command=self.update_score_label, length=400)
            scale.grid(row=1, column=0, pady=10)
            
            number_frame = ttk.Frame(scale_frame)
            number_frame.grid(row=2, column=0)
            for i in range(1, 11):
                ttk.Label(number_frame, text=str(i), font=('Arial', 8)).grid(row=0, column=i-1, padx=17)
            
            button_frame = ttk.Frame(self.question_frame)
            button_frame.grid(row=6, column=0, pady=20)
            
            if self.current_category_index > 0:
                ttk.Button(button_frame, text="← Previous", command=self.previous_question).grid(row=0, column=0, padx=5)
            
            ttk.Button(button_frame, text="Next →", command=self.next_question).grid(row=0, column=1, padx=5)
        else:
            self.show_completion_interface()
    
    def update_score_label(self, value):
        self.score_label.config(text=str(int(float(value))))
    
    def next_question(self):
        category = self.categories[self.current_category_index]
        self.scores[category] = self.score_var.get()
        self.current_category_index += 1
        self.show_question_interface()
    
    def previous_question(self):
        self.current_category_index -= 1
        category = self.categories[self.current_category_index]
        self.show_question_interface()
        if category in self.scores:
            self.score_var.set(self.scores[category])
    
    def show_completion_interface(self):
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.question_frame, text="Assessment Complete!", font=('Arial', 18, 'bold')).grid(row=0, column=0, pady=20)
        
        button_frame = ttk.Frame(self.question_frame)
        button_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(button_frame, text="View Results", command=self.generate_chart).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Save as PNG", command=self.save_chart).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Start Over", command=self.reset_assessment).grid(row=0, column=2, padx=5)
    
    def generate_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        categories = list(self.scores.keys())
        values = list(self.scores.values())
        
        num_vars = len(categories)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, label='Your Scores', color='#2E86AB')
        ax.fill(angles, values, alpha=0.25, color='#2E86AB')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=9)
        
        ax.set_ylim(0, 10)
        ax.set_yticks(range(1, 11))
        ax.set_yticklabels(range(1, 11), size=8)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        fig.suptitle('Self-Assessment Results', fontsize=18, fontweight='bold', y=0.98)
        ax.set_title(f'Assessment Date: {date_str}', size=11, pad=20)
        
        avg_score = np.mean(list(self.scores.values()))
        textstr = f'Average Score: {avg_score:.1f}/10'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        fig.text(0.5, 0.02, textstr, ha='center', fontsize=12, bbox=props)
        
        plt.tight_layout()
        
        self.chart_figure = fig
        
        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_chart(self):
        if not self.chart_figure:
            self.generate_chart()
        
        if self.chart_figure:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"self_assessment_{timestamp}.png"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                self.chart_figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Chart saved successfully to:\n{file_path}")
    
    def reset_assessment(self):
        self.scores = {}
        self.current_category_index = 0
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        self.chart_figure = None
        self.show_question_interface()


def main():
    root = tk.Tk()
    app = SelfAssessmentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime


class SelfAssessmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Development Self-Assessment")
        self.root.geometry("1200x800")
        
        self.categories = {
            "Technical Skills": [
                "Proficiency with core tools and technologies in your field",
                "Ability to learn and adapt to new technical tools",
                "Quality of technical work output",
                "Technical troubleshooting and debugging skills"
            ],
            "Interpersonal Skills": [
                "Building positive relationships with colleagues",
                "Reading social cues and understanding others",
                "Showing empathy and emotional awareness",
                "Navigating workplace dynamics effectively"
            ],
            "Communication": [
                "Clarity in written communication (emails, documents)",
                "Effectiveness in verbal communication and presentations",
                "Active listening and understanding others' points",
                "Adapting communication style to different audiences"
            ],
            "Learning Ability": [
                "Speed of understanding new concepts",
                "Ability to retain and apply what you learn",
                "Self-directed learning without guidance",
                "Learning from feedback and mistakes"
            ],
            "Leadership": [
                "Inspiring and motivating others",
                "Making decisions with confidence",
                "Delegating tasks effectively",
                "Developing and mentoring team members"
            ],
            "Problem Solving": [
                "Breaking down complex problems systematically",
                "Identifying root causes vs. symptoms",
                "Generating creative solutions",
                "Evaluating tradeoffs and making decisions"
            ],
            "Learning Habits & Development": [
                "Consistency in professional development activities",
                "Staying current with industry trends and best practices",
                "Applying new knowledge to work situations",
                "Seeking out learning opportunities proactively"
            ],
            "Emotional Intelligence": [
                "Awareness of your own emotions and triggers",
                "Understanding others' emotional states and needs",
                "Managing emotions in stressful situations",
                "Building trust and rapport with others"
            ],
            "Systems Thinking": [
                "Understanding how different parts of systems interact",
                "Seeing patterns and connections across domains",
                "Considering downstream effects of decisions",
                "Thinking strategically about long-term implications"
            ],
            "Adaptability": [
                "Adjusting to unexpected changes in plans or priorities",
                "Staying effective in ambiguous situations",
                "Pivoting strategies when circumstances change",
                "Responding constructively to criticism and feedback"
            ],
            "Time Management": [
                "Meeting deadlines consistently",
                "Accurately estimating how long tasks will take",
                "Prioritizing effectively among competing demands",
                "Minimizing procrastination and staying focused"
            ],
            "Creativity": [
                "Generating novel ideas and approaches",
                "Challenging conventional thinking constructively",
                "Thinking laterally across different domains",
                "Balancing creativity with practical constraints"
            ],
            "Collaboration": [
                "Contributing effectively in team settings",
                "Compromising and finding middle ground",
                "Giving and receiving help appropriately",
                "Handling team conflicts constructively"
            ],
            "Attention to Detail": [
                "Catching errors and inconsistencies",
                "Balancing perfectionism with pragmatism",
                "Following through on details without losing sight of goals",
                "Maintaining quality standards consistently"
            ],
            "Self-Motivation": [
                "Maintaining drive without external supervision",
                "Taking initiative to identify and solve problems",
                "Following through on commitments",
                "Sustaining energy and enthusiasm over time"
            ],
            "Decision Making": [
                "Making timely decisions with incomplete information",
                "Weighing risks and benefits systematically",
                "Standing behind your decisions with confidence",
                "Track record of sound decision outcomes"
            ],
            "Cultural Awareness": [
                "Understanding diverse perspectives and backgrounds",
                "Using inclusive behavior and language",
                "Being open to unfamiliar ideas and practices",
                "Recognizing and addressing unconscious biases"
            ],
            "Influence & Persuasion": [
                "Convincing others without formal authority",
                "Negotiating effectively to reach agreements",
                "Building consensus among stakeholders",
                "Presenting ideas compellingly"
            ]
        }
        
        self.scores = {}
        self.current_category_index = 0
        self.current_question_index = 0
        self.category_list = list(self.categories.keys())
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
    
    def get_total_questions(self):
        return sum(len(questions) for questions in self.categories.values())
    
    def get_current_question_number(self):
        total = 0
        for i in range(self.current_category_index):
            total += len(self.categories[self.category_list[i]])
        total += self.current_question_index + 1
        return total
    
    def show_question_interface(self):
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        if self.current_category_index < len(self.category_list):
            category = self.category_list[self.current_category_index]
            questions = self.categories[category]
            
            if self.current_question_index < len(questions):
                question = questions[self.current_question_index]
                
                current_q = self.get_current_question_number()
                total_q = self.get_total_questions()
                progress_text = f"Question {current_q} of {total_q}"
                ttk.Label(self.question_frame, text=progress_text, font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
                
                ttk.Label(self.question_frame, text=f"Category: {category}", font=('Arial', 14, 'bold'), foreground='#2E86AB').grid(row=1, column=0, sticky=tk.W, pady=10)
                
                ttk.Label(self.question_frame, text="Rate your professional ability:", font=('Arial', 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
                
                question_label = ttk.Label(self.question_frame, text=question, font=('Arial', 13), wraplength=800)
                question_label.grid(row=3, column=0, sticky=tk.W, pady=10)
                
                ttk.Label(self.question_frame, text="(1 = Needs Significant Improvement, 5 = Exceptional)", font=('Arial', 10, 'italic')).grid(row=4, column=0, sticky=tk.W, pady=5)
                
                scale_frame = ttk.Frame(self.question_frame)
                scale_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=20)
                
                self.score_var = tk.IntVar(value=3)
                self.score_label = ttk.Label(scale_frame, text="3", font=('Arial', 24, 'bold'))
                self.score_label.grid(row=0, column=0, pady=10)
                
                scale = ttk.Scale(scale_frame, from_=1, to=5, orient=tk.HORIZONTAL, 
                                variable=self.score_var, command=self.update_score_label, length=400)
                scale.grid(row=1, column=0, pady=10)
                
                number_frame = ttk.Frame(scale_frame)
                number_frame.grid(row=2, column=0)
                for i in range(1, 6):
                    ttk.Label(number_frame, text=str(i), font=('Arial', 8)).grid(row=0, column=i-1, padx=42)
                
                sub_q_text = f"Sub-question {self.current_question_index + 1} of {len(questions)} in this category"
                ttk.Label(self.question_frame, text=sub_q_text, font=('Arial', 9, 'italic'), foreground='gray').grid(row=6, column=0, sticky=tk.W, pady=5)
                
                button_frame = ttk.Frame(self.question_frame)
                button_frame.grid(row=7, column=0, pady=20)
                
                if self.current_category_index > 0 or self.current_question_index > 0:
                    ttk.Button(button_frame, text="← Previous", command=self.previous_question).grid(row=0, column=0, padx=5)
                
                ttk.Button(button_frame, text="Next →", command=self.next_question).grid(row=0, column=1, padx=5)
            else:
                self.current_category_index += 1
                self.current_question_index = 0
                self.show_question_interface()
        else:
            self.show_completion_interface()
    
    def update_score_label(self, value):
        self.score_label.config(text=str(int(float(value))))
    
    def next_question(self):
        category = self.category_list[self.current_category_index]
        question = self.categories[category][self.current_question_index]
        
        key = f"{category}::{question}"
        self.scores[key] = self.score_var.get()
        
        self.current_question_index += 1
        
        if self.current_question_index >= len(self.categories[category]):
            self.current_category_index += 1
            self.current_question_index = 0
        
        self.show_question_interface()
    
    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
        else:
            if self.current_category_index > 0:
                self.current_category_index -= 1
                self.current_question_index = len(self.categories[self.category_list[self.current_category_index]]) - 1
        
        category = self.category_list[self.current_category_index]
        question = self.categories[category][self.current_question_index]
        key = f"{category}::{question}"
        
        self.show_question_interface()
        if key in self.scores:
            self.score_var.set(self.scores[key])
    
    def show_completion_interface(self):
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.question_frame, text="Assessment Complete!", font=('Arial', 18, 'bold')).grid(row=0, column=0, pady=20)
        
        button_frame = ttk.Frame(self.question_frame)
        button_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(button_frame, text="View Results", command=self.generate_chart).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Details", command=self.show_detailed_results).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Save as PNG", command=self.save_chart).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Start Over", command=self.reset_assessment).grid(row=0, column=3, padx=5)
    
    def calculate_category_averages(self):
        averages = {}
        for category in self.category_list:
            category_scores = [score for key, score in self.scores.items() if key.startswith(f"{category}::")]
            if category_scores:
                averages[category] = np.mean(category_scores)
        return averages
    
    def show_detailed_results(self):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Detailed Assessment Results")
        detail_window.geometry("800x600")
        
        main_frame = ttk.Frame(detail_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_window.columnconfigure(0, weight=1)
        detail_window.rowconfigure(0, weight=1)
        
        ttk.Label(main_frame, text="Detailed Breakdown by Category", font=('Arial', 16, 'bold')).grid(row=0, column=0, pady=10, sticky=tk.W)
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Courier', 10), width=90, height=35)
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        category_averages = self.calculate_category_averages()
        
        for category in self.category_list:
            avg = category_averages.get(category, 0)
            text_widget.insert(tk.END, f"\n{'='*80}\n")
            text_widget.insert(tk.END, f"{category.upper()} - Average: {avg:.1f}/5\n")
            text_widget.insert(tk.END, f"{'='*80}\n\n")
            
            for question in self.categories[category]:
                key = f"{category}::{question}"
                score = self.scores.get(key, 0)
                text_widget.insert(tk.END, f"  [{score}/5] {question}\n\n")
        
        text_widget.config(state=tk.DISABLED)
        
        close_btn = ttk.Button(main_frame, text="Close", command=detail_window.destroy)
        close_btn.grid(row=2, column=0, pady=10)
    
    def generate_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        category_averages = self.calculate_category_averages()
        
        categories = list(category_averages.keys())
        values = list(category_averages.values())
        
        num_vars = len(categories)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2, label='Your Scores', color='#2E86AB')
        ax.fill(angles, values, alpha=0.25, color='#2E86AB')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=9)
        
        ax.set_ylim(0, 5)
        ax.set_yticks(range(1, 6))
        ax.set_yticklabels(range(1, 6), size=8)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        fig.suptitle('Self-Assessment Results', fontsize=18, fontweight='bold', y=0.98)
        ax.set_title(f'Assessment Date: {date_str}', size=11, pad=20)
        
        avg_score = np.mean(list(category_averages.values()))
        textstr = f'Overall Average Score: {avg_score:.1f}/5 | Based on {self.get_total_questions()} detailed questions'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        fig.text(0.5, 0.02, textstr, ha='center', fontsize=11, bbox=props)
        
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
        self.current_question_index = 0
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

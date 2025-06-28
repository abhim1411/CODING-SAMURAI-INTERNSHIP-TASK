#!/usr/bin/env python3
"""
GUI To-Do List Application
A comprehensive task management system with tkinter GUI and file persistence.
"""

# Test tkinter availability
try:
    import tkinter as tk
    print("✅ Tkinter imported successfully")
except ImportError as e:
    print(f"❌ Error importing tkinter: {e}")
    print("Please install tkinter or use a Python version with tkinter included")
    exit(1)
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from typing import List, Dict

class TodoGUI:
    def __init__(self):
        self.filename = "tasks.json"
        self.tasks = self.load_tasks()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("📝 Personal To-Do List Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load initial tasks
        self.refresh_task_list()
        
        # Update statistics
        self.update_stats()
    
    def setup_styles(self):
        """Configure ttk styles for better appearance."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Custom.Treeview', font=('Arial', 10))
        style.configure('Custom.Treeview.Heading', font=('Arial', 11, 'bold'))
    
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main title
        title_label = ttk.Label(self.root, text="🎯 Personal To-Do List Manager", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel for controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Add task section
        self.create_add_task_section(left_panel)
        
        # Control buttons section
        self.create_control_buttons(left_panel)
        
        # Statistics section
        self.create_stats_section(left_panel)
        
        # Right panel for task list
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Task list section
        self.create_task_list_section(right_panel)
    
    def create_add_task_section(self, parent):
        """Create the add task section."""
        # Add Task Frame
        add_frame = ttk.LabelFrame(parent, text="📝 Add New Task", padding=10)
        add_frame.pack(fill='x', pady=(0, 10))
        
        # Task description
        ttk.Label(add_frame, text="Task Description:").pack(anchor='w')
        self.task_entry = tk.Text(add_frame, height=3, width=30, wrap='word')
        self.task_entry.pack(fill='x', pady=(2, 10))
        
        # Priority selection
        ttk.Label(add_frame, text="Priority:").pack(anchor='w')
        self.priority_var = tk.StringVar(value="Medium")
        priority_frame = ttk.Frame(add_frame)
        priority_frame.pack(fill='x', pady=(2, 10))
        
        priorities = [("High", "High"), ("Medium", "Medium"), ("Low", "Low")]
        for text, value in priorities:
            ttk.Radiobutton(priority_frame, text=text, variable=self.priority_var, 
                           value=value).pack(side='left', padx=(0, 10))
        
        # Add button
        ttk.Button(add_frame, text="➕ Add Task", command=self.add_task,
                  style='Accent.TButton').pack(fill='x')
    
    def create_control_buttons(self, parent):
        """Create control buttons section."""
        control_frame = ttk.LabelFrame(parent, text="🎮 Task Controls", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))
        
        buttons = [
            ("✅ Complete Task", self.complete_task),
            ("❌ Delete Task", self.delete_task),
            ("🔍 Search Tasks", self.search_tasks),
            ("🔄 Refresh List", self.refresh_task_list),
        ]
        
        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(fill='x', pady=2)
    
    def create_stats_section(self, parent):
        """Create statistics section."""
        stats_frame = ttk.LabelFrame(parent, text="📊 Statistics", padding=10)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="Loading...", justify='left')
        self.stats_label.pack(anchor='w')
    
    def create_task_list_section(self, parent):
        """Create task list section with treeview."""
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:", style='Heading.TLabel').pack(side='left')
        
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All", "Pending", "Completed", "High Priority"]
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=filter_options, state='readonly', width=15)
        filter_combo.pack(side='left', padx=(10, 0))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Task list frame
        list_frame = ttk.LabelFrame(parent, text="📋 Task List", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Status', 'Priority', 'Description', 'Created')
        self.task_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                     style='Custom.Treeview')
        
        # Configure columns
        self.task_tree.heading('ID', text='ID')
        self.task_tree.heading('Status', text='Status')
        self.task_tree.heading('Priority', text='Priority')
        self.task_tree.heading('Description', text='Description')
        self.task_tree.heading('Created', text='Created')
        
        self.task_tree.column('ID', width=50, anchor='center')
        self.task_tree.column('Status', width=80, anchor='center')
        self.task_tree.column('Priority', width=80, anchor='center')
        self.task_tree.column('Description', width=300, anchor='w')
        self.task_tree.column('Created', width=150, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.task_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.task_tree.xview)
        
        self.task_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.task_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.task_tree.bind('<Double-1>', self.on_task_double_click)
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_tasks(self):
        """Save tasks to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save tasks: {e}")
    
    def add_task(self):
        """Add a new task."""
        description = self.task_entry.get("1.0", tk.END).strip()
        
        if not description:
            messagebox.showwarning("Warning", "Please enter a task description!")
            return
        
        task = {
            "id": max([t.get("id", 0) for t in self.tasks], default=0) + 1,
            "description": description,
            "priority": self.priority_var.get().lower(),
            "completed": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.tasks.append(task)
        self.save_tasks()
        
        # Clear entry and refresh
        self.task_entry.delete("1.0", tk.END)
        self.refresh_task_list()
        self.update_stats()
        
        messagebox.showinfo("Success", f"Task '{description[:30]}...' added successfully!")
    
    def complete_task(self):
        """Mark selected task as completed."""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to complete!")
            return
        
        item = self.task_tree.item(selected[0])
        task_id = int(item['values'][0])
        
        for task in self.tasks:
            if task["id"] == task_id:
                if task["completed"]:
                    messagebox.showinfo("Info", "Task is already completed!")
                    return
                
                task["completed"] = True
                task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_tasks()
                self.refresh_task_list()
                self.update_stats()
                
                messagebox.showinfo("Success", f"Task completed successfully!")
                return
    
    def delete_task(self):
        """Delete selected task."""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return
        
        item = self.task_tree.item(selected[0])
        task_id = int(item['values'][0])
        task_desc = item['values'][3]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete:\n'{task_desc[:50]}...'?"):
            
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self.save_tasks()
            self.refresh_task_list()
            self.update_stats()
            
            messagebox.showinfo("Success", "Task deleted successfully!")
    
    def search_tasks(self):
        """Search tasks by keyword."""
        keyword = simpledialog.askstring("Search Tasks", "Enter search keyword:")
        if not keyword:
            return
        
        keyword = keyword.lower()
        matching_tasks = [t for t in self.tasks if keyword in t["description"].lower()]
        
        if not matching_tasks:
            messagebox.showinfo("Search Results", f"No tasks found containing '{keyword}'")
            return
        
        # Create search results window
        self.show_search_results(matching_tasks, keyword)
    
    def show_search_results(self, tasks, keyword):
        """Show search results in a new window."""
        search_window = tk.Toplevel(self.root)
        search_window.title(f"Search Results for '{keyword}'")
        search_window.geometry("600x400")
        
        # Create treeview for results
        columns = ('ID', 'Status', 'Priority', 'Description')
        results_tree = ttk.Treeview(search_window, columns=columns, show='headings')
        
        for col in columns:
            results_tree.heading(col, text=col)
            if col == 'Description':
                results_tree.column(col, width=300, anchor='w')
            else:
                results_tree.column(col, width=80, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(search_window, orient='vertical', command=results_tree.yview)
        results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate results
        for task in tasks:
            status = "✅ Done" if task["completed"] else "⏳ Pending"
            priority = task["priority"].title()
            
            results_tree.insert('', 'end', values=(
                task["id"], status, priority, task["description"]
            ))
    
    def refresh_task_list(self):
        """Refresh the task list based on current filter."""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Filter tasks
        filter_type = self.filter_var.get()
        filtered_tasks = self.tasks.copy()
        
        if filter_type == "Pending":
            filtered_tasks = [t for t in self.tasks if not t["completed"]]
        elif filter_type == "Completed":
            filtered_tasks = [t for t in self.tasks if t["completed"]]
        elif filter_type == "High Priority":
            filtered_tasks = [t for t in self.tasks if t["priority"] == "high" and not t["completed"]]
        
        # Sort tasks (high priority first, then by ID)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        filtered_tasks.sort(key=lambda x: (priority_order.get(x["priority"], 1), x["id"]))
        
        # Populate treeview
        for task in filtered_tasks:
            status = "✅ Done" if task["completed"] else "⏳ Pending"
            priority = task["priority"].title()
            created = task["created"].split()[0]  # Show only date
            
            # Color coding based on priority and status
            tags = []
            if task["completed"]:
                tags.append("completed")
            elif task["priority"] == "high":
                tags.append("high_priority")
            
            self.task_tree.insert('', 'end', values=(
                task["id"], status, priority, task["description"], created
            ), tags=tags)
        
        # Configure tags for color coding
        self.task_tree.tag_configure("completed", foreground="gray")
        self.task_tree.tag_configure("high_priority", foreground="red", font=('Arial', 10, 'bold'))
    
    def update_stats(self):
        """Update statistics display."""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["completed"]])
        pending = total - completed
        high_priority = len([t for t in self.tasks if t["priority"] == "high" and not t["completed"]])
        
        stats_text = f"Total Tasks: {total}\n"
        stats_text += f"Completed: {completed}\n"
        stats_text += f"Pending: {pending}\n"
        stats_text += f"High Priority: {high_priority}\n"
        
        if total > 0:
            completion_rate = (completed / total) * 100
            stats_text += f"Progress: {completion_rate:.1f}%"
        
        self.stats_label.config(text=stats_text)
    
    def on_task_double_click(self, event):
        """Handle double-click on task (show details)."""
        selected = self.task_tree.selection()
        if not selected:
            return
        
        item = self.task_tree.item(selected[0])
        task_id = int(item['values'][0])
        
        # Find the task
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        
        # Show task details
        self.show_task_details(task)
    
    def show_task_details(self, task):
        """Show detailed task information in a popup."""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Task Details - ID {task['id']}")
        details_window.geometry("400x300")
        details_window.resizable(False, False)
        
        # Task details
        ttk.Label(details_window, text="Task Details", style='Title.TLabel').pack(pady=10)
        
        details_frame = ttk.Frame(details_window)
        details_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        details = [
            ("ID:", str(task["id"])),
            ("Status:", "✅ Completed" if task["completed"] else "⏳ Pending"),
            ("Priority:", task["priority"].title()),
            ("Created:", task["created"]),
        ]
        
        if task["completed"]:
            details.append(("Completed:", task.get("completed_date", "Unknown")))
        
        for label, value in details:
            row_frame = ttk.Frame(details_frame)
            row_frame.pack(fill='x', pady=2)
            ttk.Label(row_frame, text=label, font=('Arial', 10, 'bold')).pack(side='left')
            ttk.Label(row_frame, text=value).pack(side='left', padx=(10, 0))
        
        # Description
        ttk.Label(details_frame, text="Description:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        desc_text = tk.Text(details_frame, height=6, width=40, wrap='word', state='disabled')
        desc_text.pack(fill='both', expand=True)
        
        desc_text.config(state='normal')
        desc_text.insert('1.0', task["description"])
        desc_text.config(state='disabled')
        
        # Close button
        ttk.Button(details_window, text="Close", 
                  command=details_window.destroy).pack(pady=10)
    
    def run(self):
        """Start the GUI application."""
        print("🚀 Starting GUI application...")
        
        # Set window icon (if available)
        try:
            self.root.iconname("Todo")
        except:
            pass
        
        # Force window to appear
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        print("✅ GUI window should now be visible!")
        print("📝 If you don't see the window, try running from external terminal")
        
        # Start main loop
        self.root.mainloop()

def main():
    """Main function to run the application."""
    try:
        app = TodoGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
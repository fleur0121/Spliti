# UI components and display functions for the chat client

import tkinter as tk


class ChatUI:
    def __init__(self, root):
        self.root = root
        self.colors = {
            "bg": "#FFF5F8",
            "panel": "#FFE6F0",
            "accent": "#FFB3C7",
            "accent_dark": "#FF7AA2",
            "mint": "#D8F8E1",
            "mint_dark": "#7BD88F",
            "lavender": "#F1E7FF",
            "sky": "#E8F6FF",
            "cream": "#FFF7E3",
            "text": "#3B3B3B",
            "white": "#FFFFFF",
            "shadow": "#F7C6D6",
            "line_bg": "#F7F4EE",
        }

        root.option_add("*Button.borderWidth", 0)
        root.option_add("*Button.highlightThickness", 0)
        root.option_add("*Entry.highlightThickness", 0)
        root.option_add("*Listbox.highlightThickness", 0)
        root.option_add("*Text.highlightThickness", 0)
        root.option_add("*Scrollbar.borderWidth", 0)

        def make_button(parent, text, command, bg, fg, font):
            return tk.Button(
                parent,
                text=text,
                command=command,
                bg=bg,
                fg=fg,
                activebackground=self.colors["panel"],
                activeforeground=fg,
                font=font,
                relief=tk.FLAT,
                bd=0,
                highlightthickness=0,
                highlightbackground=self.colors["panel"],
                highlightcolor=self.colors["panel"],
                takefocus=0,
                overrelief=tk.FLAT,
            )

        # Top banner
        banner = tk.Frame(
            root, bg=self.colors["panel"], highlightthickness=0, bd=0
        )
        banner.pack(fill=tk.X, padx=12, pady=(12, 6))

        title = tk.Label(
            banner,
            text="TermKaiwa",
            bg=self.colors["panel"],
            fg=self.colors["accent_dark"],
            font=("Comic Sans MS", 18, "bold"),
        )
        subtitle = tk.Label(
            banner,
            text="Tiny chat app 🌷",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Comic Sans MS", 10),
        )

        flower_canvas = tk.Canvas(
            banner,
            width=120,
            height=42,
            bg=self.colors["panel"],
            highlightthickness=0,
        )

        # Simple function to draw a flower shape on the canvas
        def draw_flower(canvas, x, y, petal, center, scale=1.0):
            r = 7 * scale
            canvas.create_oval(
                x - r, y - r, x + r, y + r, fill=center, outline=""
            )
            offsets = [(-10, 0), (10, 0), (0, -10), (0, 10)]
            for dx, dy in offsets:
                canvas.create_oval(
                    x + dx - r,
                    y + dy - r,
                    x + dx + r,
                    y + dy + r,
                    fill=petal,
                    outline="",
                )

        draw_flower(flower_canvas, 20, 20, "#FFC6DD", "#FFDF6E", 0.9)
        draw_flower(flower_canvas, 55, 18, "#CDE7FF", "#FFD9F0", 0.8)
        draw_flower(flower_canvas, 90, 22, "#EAD7FF", "#FFE8A3", 0.95)

        title.pack(anchor="w", padx=10, pady=(6, 0))
        subtitle.pack(anchor="w", padx=10, pady=(0, 6))
        flower_canvas.pack(side=tk.RIGHT, padx=10, pady=6)

        # Main layout
        main_frame = tk.Frame(
            root, bg=self.colors["bg"], highlightthickness=0, bd=0
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

        left_panel = tk.Frame(
            main_frame, bg=self.colors["bg"], highlightthickness=0, bd=0
        )
        right_panel = tk.Frame(
            main_frame,
            bg=self.colors["panel"],
            width=220,
            relief=tk.FLAT,
            highlightthickness=0,
            bd=0,
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # View selector
        view_frame = tk.Frame(
            left_panel, bg=self.colors["bg"], highlightthickness=0, bd=0
        )
        self.view_label = tk.Label(
            view_frame,
            text="Now chatting: Public",
            bg=self.colors["bg"],
            fg=self.colors["accent_dark"],
            font=("Comic Sans MS", 10, "bold"),
        )
        self.public_view_btn = make_button(
            view_frame,
            "🌸 Public",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.secret_view_btn = make_button(
            view_frame,
            "🔒 Secret",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.view_label.pack(side=tk.LEFT, padx=(2, 8))
        self.public_view_btn.pack(side=tk.LEFT, padx=4)
        self.secret_view_btn.pack(side=tk.LEFT, padx=4)
        view_frame.pack(fill=tk.X, padx=2, pady=(0, 6))

        # Chat display
        frame = tk.Frame(
            left_panel, bg=self.colors["bg"], highlightthickness=0, bd=0
        )
        self.chat_text = tk.Text(
            frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.colors["line_bg"],
            fg=self.colors["text"],
            font=("Comic Sans MS", 10),
            padx=14,
            pady=14,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            highlightbackground=self.colors["line_bg"],
        )
        scrollbar = tk.Scrollbar(
            frame,
            command=self.chat_text.yview,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
        )
        self.chat_text.config(yscrollcommand=scrollbar.set)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 10))

        # Tags
        self.chat_text.tag_configure(
            "server",
            foreground=self.colors["accent_dark"],
            background=self.colors["panel"],
            font=("Comic Sans MS", 9, "bold"),
            spacing1=10,
            spacing3=10,
            lmargin1=180,
            lmargin2=180,
            rmargin=180,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "server_time",
            foreground="#C7899B",
            background=self.colors["panel"],
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=180,
            lmargin2=180,
            rmargin=180,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "you_sender",
            foreground="#3F8D54",
            background=self.colors["mint"],
            font=("Comic Sans MS", 8, "bold"),
            spacing1=10,
            spacing3=0,
            lmargin1=280,
            lmargin2=280,
            rmargin=24,
            justify=tk.RIGHT,
        )
        self.chat_text.tag_configure(
            "you",
            foreground=self.colors["mint_dark"],
            background=self.colors["mint"],
            font=("Comic Sans MS", 11, "bold"),
            spacing1=2,
            spacing3=2,
            lmargin1=280,
            lmargin2=280,
            rmargin=24,
            justify=tk.RIGHT,
        )
        self.chat_text.tag_configure(
            "you_time",
            foreground="#5AA06A",
            background=self.colors["mint"],
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=280,
            lmargin2=280,
            rmargin=24,
            justify=tk.RIGHT,
        )
        self.chat_text.tag_configure(
            "dm_in",
            foreground="#7A4DD8",
            background=self.colors["lavender"],
            font=("Comic Sans MS", 11),
            spacing1=2,
            spacing3=2,
            lmargin1=24,
            lmargin2=24,
            rmargin=280,
        )
        self.chat_text.tag_configure(
            "dm_in_sender",
            foreground="#6B44BB",
            background=self.colors["lavender"],
            font=("Comic Sans MS", 8, "bold"),
            spacing1=10,
            spacing3=0,
            lmargin1=24,
            lmargin2=24,
            rmargin=280,
        )
        self.chat_text.tag_configure(
            "dm_in_time",
            foreground="#9C7EDB",
            background=self.colors["lavender"],
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=24,
            lmargin2=24,
            rmargin=280,
        )
        self.chat_text.tag_configure(
            "dm_out",
            foreground="#7A4DD8",
            background=self.colors["lavender"],
            font=("Comic Sans MS", 11),
            spacing1=2,
            spacing3=2,
            lmargin1=280,
            lmargin2=280,
            rmargin=24,
            justify=tk.RIGHT,
        )
        self.chat_text.tag_configure(
            "dm_out_sender",
            foreground="#6B44BB",
            background=self.colors["lavender"],
            font=("Comic Sans MS", 8, "bold"),
            spacing1=10,
            spacing3=0,
            lmargin1=280,
            lmargin2=280,
            rmargin=24,
            justify=tk.RIGHT,
        )
        self.chat_text.tag_configure(
            "dm_out_time",
            foreground="#9C7EDB",
            background=self.colors["lavender"],
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=280,
            lmargin2=280,
            rmargin=24,
            justify=tk.RIGHT,
        )
        self.chat_text.tag_configure(
            "join_leave",
            foreground="#C27700",
            background=self.colors["cream"],
            font=("Comic Sans MS", 9, "bold"),
            spacing1=10,
            spacing3=10,
            lmargin1=210,
            lmargin2=210,
            rmargin=210,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "join_leave_time",
            foreground="#D39C46",
            background=self.colors["cream"],
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=210,
            lmargin2=210,
            rmargin=210,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "error",
            foreground="#B00020",
            background="#FFE5EA",
            font=("Comic Sans MS", 9, "bold"),
            spacing1=10,
            spacing3=10,
            lmargin1=170,
            lmargin2=170,
            rmargin=170,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "error_time",
            foreground="#CC6B7F",
            background="#FFE5EA",
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=170,
            lmargin2=170,
            rmargin=170,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "chat",
            foreground=self.colors["text"],
            background=self.colors["sky"],
            font=("Comic Sans MS", 11),
            spacing1=2,
            spacing3=2,
            lmargin1=24,
            lmargin2=24,
            rmargin=280,
        )
        self.chat_text.tag_configure(
            "chat_sender",
            foreground="#53748C",
            background=self.colors["sky"],
            font=("Comic Sans MS", 8, "bold"),
            spacing1=10,
            spacing3=0,
            lmargin1=24,
            lmargin2=24,
            rmargin=280,
        )
        self.chat_text.tag_configure(
            "chat_time",
            foreground="#6F8B9B",
            background=self.colors["sky"],
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=24,
            lmargin2=24,
            rmargin=280,
        )
        self.chat_text.tag_configure(
            "local",
            foreground="#0D7F87",
            background="#D9FEFF",
            font=("Comic Sans MS", 9, "bold"),
            spacing1=10,
            spacing3=10,
            lmargin1=170,
            lmargin2=170,
            rmargin=170,
            justify=tk.CENTER,
        )
        self.chat_text.tag_configure(
            "local_time",
            foreground="#5FA8AD",
            background="#D9FEFF",
            font=("Comic Sans MS", 8),
            spacing1=0,
            spacing3=10,
            lmargin1=170,
            lmargin2=170,
            rmargin=170,
            justify=tk.CENTER,
        )

        # Toolbar
        toolbar = tk.Frame(
            left_panel, bg=self.colors["bg"], highlightthickness=0, bd=0
        )
        self.users_btn = make_button(
            toolbar,
            "👥 Users",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.dm_btn = make_button(
            toolbar,
            "💌 DM",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.rename_btn = make_button(
            toolbar,
            "✏️ Rename",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.secret_btn = make_button(
            toolbar,
            "🔒 Secret",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.mute_btn = make_button(
            toolbar,
            "🔇 Mute",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.quit_btn = make_button(
            toolbar,
            "👋 Quit",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.users_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.dm_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.rename_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.secret_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.mute_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.quit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        toolbar.pack(fill=tk.X)

        # Bottom input
        bottom_frame = tk.Frame(
            left_panel, bg=self.colors["bg"], highlightthickness=0, bd=0
        )
        self.entry = tk.Entry(
            bottom_frame,
            font=("Comic Sans MS", 10),
            relief=tk.FLAT,
            bg=self.colors["white"],
            fg=self.colors["text"],
            insertbackground=self.colors["accent_dark"],
            bd=0,
            highlightthickness=0,
            highlightbackground=self.colors["white"],
        )
        self.send_button = make_button(
            bottom_frame,
            "📤 Send",
            lambda: None,
            self.colors["mint"],
            self.colors["text"],
            ("Comic Sans MS", 10, "bold"),
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)
        bottom_frame.pack(fill=tk.X, padx=2, pady=(0, 10))

        # Right panel
        status_frame = tk.Frame(
            right_panel, bg=self.colors["panel"], highlightthickness=0, bd=0
        )
        status_frame.pack(fill=tk.X, padx=10, pady=(10, 4))

        self.status_label = tk.Label(
            status_frame,
            text="Status: Disconnected",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Comic Sans MS", 10, "bold"),
        )
        self.status_label.pack(anchor="w")

        self.connect_btn = make_button(
            status_frame,
            "🔌 Connect",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.disconnect_btn = make_button(
            status_frame,
            "⛔ Disconnect",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.connect_btn.pack(fill=tk.X, pady=(6, 2))
        self.disconnect_btn.pack(fill=tk.X, pady=(2, 0))

        users_frame = tk.Frame(
            right_panel, bg=self.colors["panel"], highlightthickness=0, bd=0
        )
        users_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        users_title = tk.Label(
            users_frame,
            text="Online Users",
            bg=self.colors["panel"],
            fg=self.colors["accent_dark"],
            font=("Comic Sans MS", 10, "bold"),
        )
        users_title.pack(anchor="w", pady=(0, 4))

        self.users_container = tk.Frame(
            users_frame,
            bg=self.colors["white"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
        )
        self.users_container.pack(fill=tk.BOTH, expand=True)

        self.users_refresh = make_button(
            users_frame,
            "🔄 Refresh",
            lambda: None,
            self.colors["accent"],
            self.colors["text"],
            ("Comic Sans MS", 9),
        )
        self.users_refresh.pack(fill=tk.X, pady=(6, 0))

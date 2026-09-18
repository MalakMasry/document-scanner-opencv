import os
import cv2
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from scanner import scan_image, load_image

ctk.set_appearance_mode("Dark")


class ModernScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Document Scanner")
        self.geometry("1180x760")
        self.minsize(1050, 680)

        self.BG_DARK = "#0B0F17"
        self.CARD_BG = "#131C2E"
        self.BORDER_COLOR = "#1E293B"
        self.ACCENT_CYAN = "#0EA5E9"
        self.CYAN_HOVER = "#0284C7"

        self.ACCENT_INDIGO = "#6366F1"    
        self.INDIGO_HOVER = "#4F46E5"
        
        self.TEXT_MUTED = "#64748B"

        self.configure(fg_color=self.BG_DARK)

        self.current_image_path = None
        self.scanned_image = None

        self.grid_columnconfigure((0, 1), weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.setup_header()
        self.setup_left_card()
        self.setup_right_card()


    def setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=28, pady=(20, 10), sticky="ew")

        title_label = ctk.CTkLabel(
            header_frame,
            text="📄 Document Scanner",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#F8FAFC"
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="By Malak Nabil",
            font=ctk.CTkFont(size=12),
            text_color=self.TEXT_MUTED
        )
        subtitle_label.pack(side="right", pady=(8, 0))


    def setup_left_card(self):
        self.left_card = ctk.CTkFrame(
            self,
            fg_color=self.CARD_BG,
            border_width=1,
            border_color=self.BORDER_COLOR,
            corner_radius=16
        )
        self.left_card.grid(row=1, column=0, padx=(28, 12), pady=(0, 25), sticky="nsew")
        self.left_card.grid_rowconfigure(1, weight=1)
        self.left_card.grid_columnconfigure(0, weight=1)

        lbl_title = ctk.CTkLabel(
            self.left_card,
            text="1. Source Image",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F1F5F9"
        )
        lbl_title.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.preview_frame_left = ctk.CTkFrame(
            self.left_card,
            fg_color=self.BG_DARK,
            corner_radius=12
        )
        self.preview_frame_left.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.preview_frame_left.pack_propagate(False)

        self.lbl_original_preview = ctk.CTkLabel(
            self.preview_frame_left,
            text="📁 Browse an image to load",
            font=ctk.CTkFont(size=14),
            text_color=self.TEXT_MUTED
        )
        self.lbl_original_preview.pack(expand=True)

        self.btn_browse = ctk.CTkButton(
            self.left_card,
            text="📂 Browse File",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.ACCENT_CYAN,
            hover_color=self.CYAN_HOVER,
            height=42,
            corner_radius=10,
            command=self.browse_file
        )
        self.btn_browse.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    def setup_right_card(self):
        self.right_card = ctk.CTkFrame(
            self,
            fg_color=self.CARD_BG,
            border_width=1,
            border_color=self.BORDER_COLOR,
            corner_radius=16
        )
        self.right_card.grid(row=1, column=1, padx=(12, 28), pady=(0, 25), sticky="nsew")
        self.right_card.grid_rowconfigure(2, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        header_bar = ctk.CTkFrame(self.right_card, fg_color="transparent")
        header_bar.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        lbl_title = ctk.CTkLabel(
            header_bar,
            text="2. Scanned Output",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F1F5F9"
        )
        lbl_title.pack(side="left")

        self.btn_scan = ctk.CTkButton(
            header_bar,
            text="Scan",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF",
            fg_color=self.ACCENT_INDIGO,
            hover_color=self.INDIGO_HOVER,
            width=100,
            height=34,
            corner_radius=8,
            state="disabled",
            command=self.process_scan
        )
        self.btn_scan.pack(side="right")

        self.preview_frame_right = ctk.CTkFrame(
            self.right_card,
            fg_color=self.BG_DARK,
            corner_radius=12
        )
        self.preview_frame_right.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.preview_frame_right.pack_propagate(False)

        self.lbl_scanned_preview = ctk.CTkLabel(
            self.preview_frame_right,
            text="Processed document will appear here",
            font=ctk.CTkFont(size=14),
            text_color=self.TEXT_MUTED
        )
        self.lbl_scanned_preview.pack(expand=True)

        save_container = ctk.CTkFrame(self.right_card, fg_color="transparent")
        save_container.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        self.entry_filename = ctk.CTkEntry(
            save_container,
            placeholder_text="Enter file name (e.g. document_scanned.jpg)",
            height=42,
            corner_radius=10,
            border_color=self.BORDER_COLOR,
            fg_color=self.BG_DARK
        )
        self.entry_filename.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.btn_save = ctk.CTkButton(
            save_container,
            text="💾 Save As...",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            corner_radius=10,
            state="disabled",
            command=self.save_scanned_image
        )
        self.btn_save.pack(side="right")


    def resize_for_preview(self, cv2_img, max_size=(460, 440)):
        if len(cv2_img.shape) == 2:
            pil_img = Image.fromarray(cv2_img)
        else:
            rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)

        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.current_image_path = file_path
            img = load_image(file_path)

            ctk_img = self.resize_for_preview(img)
            self.lbl_original_preview.configure(image=ctk_img, text="")
            self.lbl_original_preview.image = ctk_img

            self.btn_scan.configure(state="normal")
            default_name = f"scanned_{os.path.basename(file_path)}"
            self.entry_filename.delete(0, "end")
            self.entry_filename.insert(0, default_name)

    def process_scan(self):
        if not self.current_image_path:
            return

        try:
            self.scanned_image = scan_image(self.current_image_path)

            ctk_img = self.resize_for_preview(self.scanned_image)
            self.lbl_scanned_preview.configure(image=ctk_img, text="")
            self.lbl_scanned_preview.image = ctk_img

            self.btn_save.configure(state="normal")

        except ValueError as err:
            messagebox.showerror("Scanning Error", str(err))

    def save_scanned_image(self):
        if self.scanned_image is None:
            return

        suggested_name = self.entry_filename.get().strip() or "scanned_doc.jpg"

        save_path = filedialog.asksaveasfilename(
            title="Save Document",
            initialfile=suggested_name,
            defaultextension=".jpg",
            filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png"), ("All Files", "*.*")]
        )

        if save_path:
            cv2.imwrite(save_path, self.scanned_image)
            messagebox.showinfo("Saved", f"File saved successfully to:\n{save_path}")


if __name__ == "__main__":
    app = ModernScannerApp()
    app.mainloop()
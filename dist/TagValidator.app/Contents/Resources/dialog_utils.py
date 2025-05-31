"""
Este arquivo contém utilitários para exibição de diálogos e notificações na interface.
Responsabilidades:
- Criação de diálogos personalizados para exibição de informações
- Formatação consistente para notificações de sucesso/erro/aviso
- Apresentação de resultados e confirmações ao usuário

Estas funcionalidades são usadas para interagir com o usuário durante o processo
de monitoramento e análise de dispositivos.
"""

import tkinter as tk

class DialogHelper:
    """
    Utilitário para criar e gerenciar diálogos personalizados.
    """

    @staticmethod
    def show_success_dialog(parent, title, message, path, count):
        """
        Exibe um diálogo de sucesso personalizado.

        Args:
            parent (tk.Tk): Janela pai
            title (str): Título do diálogo
            message (str): Mensagem principal
            path (str): Caminho para exibir
            count (int): Contagem a exibir
        """
        success_dialog = tk.Toplevel(parent)
        success_dialog.title(title)
        success_dialog.transient(parent)
        success_dialog.geometry("400x250")
        success_dialog.configure(bg="#f0f0f0")
        success_dialog.grab_set()  # Torna o diálogo modal

        # Adiciona ícone de sucesso
        success_icon = tk.Label(success_dialog, text="✅", font=("Arial", 30), bg="#f0f0f0", fg="#4CAF50")
        success_icon.pack(pady=(20, 10))

        # Título da mensagem
        title_label = tk.Label(success_dialog, text=message, 
                        font=("Arial", 14, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 15))

        # Local de salvamento
        path_frame = tk.Frame(success_dialog, bg="#f0f0f0")
        path_frame.pack(fill="x", padx=30, pady=5)

        path_label = tk.Label(path_frame, text=f"Pasta: {path}", 
                        font=("Arial", 10), bg="#f0f0f0", fg="#555555",
                        wraplength=350, justify="center")
        path_label.pack()

        # Total de funcionalidades
        func_label = tk.Label(success_dialog, text=f"Total de funcionalidades: {count}", 
                        font=("Arial", 10), bg="#f0f0f0")
        func_label.pack(pady=15)

        # Botão OK 
        ok_btn = tk.Button(success_dialog, text="OK", command=success_dialog.destroy, 
                        width=10, bg="#4285F4", fg="black",
                        font=("Arial", 11), relief="flat")
        ok_btn.pack(pady=10)

        # Centraliza o diálogo
        success_dialog.update_idletasks()
        width = success_dialog.winfo_width()
        height = success_dialog.winfo_height()
        x = (parent.winfo_width() // 2) - (width // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (height // 2) + parent.winfo_y()
        success_dialog.geometry(f"+{x}+{y}")

    @staticmethod
    def show_empty_logs_dialog(parent):
        """
        Exibe um diálogo informando que não há logs para salvar.

        Args:
            parent (tk.Tk): Janela pai
        """
        dialog = tk.Toplevel(parent)
        dialog.title("Aviso")
        dialog.transient(parent)
        dialog.geometry("400x200")
        dialog.configure(bg="#363636")
        dialog.grab_set()  # Torna o diálogo modal

        # Adiciona ícone e mensagem
        icon_frame = tk.Frame(dialog, bg="#363636")
        icon_frame.pack(pady=(20, 10))

        # Adiciona ícone ou imagem
        rocket_label = tk.Label(icon_frame, text="🚀", font=("Arial", 30), bg="#363636", fg="white")
        rocket_label.pack()

        msg_label = tk.Label(dialog, text="Não há logs para salvar", 
                        font=("Arial", 14), bg="#363636", fg="white")
        msg_label.pack(pady=10)

        # Botão OK
        ok_btn = tk.Button(dialog, text="OK", command=dialog.destroy, 
                        width=15, height=1, bg="#4285F4", fg="black", 
                        font=("Arial", 12), relief="flat")
        ok_btn.pack(pady=20)

        # Centraliza o diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (parent.winfo_width() // 2) - (width // 2) + parent.winfo_x()
        y = (parent.winfo_height() // 2) - (height // 2) + parent.winfo_y()
        dialog.geometry(f"+{x}+{y}")
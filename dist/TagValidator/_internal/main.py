# Ponto de entrada principal
from tag_validator import TagValidator
from ui_theme import ValidationApp



def main():
    # Inicializa e executa a aplicação
    validator = TagValidator()

    app = ValidationApp(validator)
    app.run()

if __name__ == "__main__":
    main()
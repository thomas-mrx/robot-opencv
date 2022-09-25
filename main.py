from src.app import App

if __name__ == '__main__':
    print("started")

    app = App("Playground")
    app.loop()

    print("stopped")

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window


Window.size = (1024, 600)


class Container(GridLayout):
    pass


class MyApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    MyApp().run()

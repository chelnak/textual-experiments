from __future__ import annotations

from rich import box
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Button, ButtonPressed
from textual.widgets._button import ButtonRenderable


class ButtonWidget(Button):

    mouse_over: bool = Reactive(False)
    toggle: bool = Reactive(False)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def render(self) -> RenderableType:

        text_style = Style(underline=self.toggle)

        border_style = Style(
            color="yellow" if self.toggle else "green",
            dim=self.mouse_over or self.toggle,
        )

        self.label.stylize(style=text_style)
        panel_content = ButtonRenderable(self.label)

        box_style = box.DOUBLE_EDGE if self.toggle else box.SQUARE

        return Panel(
            panel_content,
            box=box_style,
            border_style=border_style,
            expand=True,
            height=5,
            width=15,
        )


class ButtonApp(App):

    current_button: ButtonWidget | None = None
    labels = ["one", "two", "three"]

    async def on_mount(self) -> None:
        buttons = [ButtonWidget(label=Text(text=l)) for l in self.labels]
        await self.view.dock(*buttons, edge="left")

    async def handle_button_pressed(self, message: ButtonPressed):
        if self.current_button and self.current_button.name == message.sender.name:
            self.log(f"{message.sender.name} is already toggled.")
            return

        if self.current_button:
            self.current_button.toggle = False

        self.current_button = message.sender
        assert isinstance(self.current_button, ButtonWidget)
        self.current_button.toggle = True

        self.log(f"Button {message.sender.name} pressed")

        await self.view.refresh_layout()


if __name__ == "__main__":
    """Basic buttons (WIP)."""
    ButtonApp.run(title="Buttons")

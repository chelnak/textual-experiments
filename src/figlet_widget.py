from typing import Optional

from rich.align import Align
from rich.console import RenderableType, Console, ConsoleOptions, RenderResult
from rich.style import Style
from rich.text import Text

from textual.widget import Widget
from textual.reactive import Reactive

from pyfiglet import Figlet


class FigletTextRenderable:
    """A renderable to generate figlet text that adapts to fit the container.
    The class originates from here: https://github.com/willmcgugan/textual/blob/f47b3e089c681275c48c0debc7a320b66a772a50/examples/calculator.py#L27
    """

    def __init__(self, text: str) -> None:
        self.text = text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Build a Rich renderable to render the Figlet text."""
        size = min(options.max_width / 2, options.max_height)
        if size < 4:
            yield Text(self.text, style="bold")
        else:
            if size < 7:
                font_name = "mini"
            elif size < 8:
                font_name = "small"
            elif size < 10:
                font_name = "standard"
            else:
                font_name = "big"
            font = Figlet(font=font_name, width=options.max_width)
            yield Text(font.renderText(self.text).rstrip("\n"), style="bold")


class FigletTextWidget(Widget):
    """A widget that will generate and display figlet text."""

    has_focus = Reactive(False)
    mouse_over: bool = Reactive(False)

    def __init__(
        self,
        text: str,
        name: Optional[str] = None,
        style: Optional[Style] = None,
        layout_size: int = 8,
    ) -> None:
        """A widget that will generate and display figlet text.

        Args:
            text (str, optional): The text that will be rendered in the widget.
            name (str, optional): The name of the widget. Defaults to the name of the class.
            style (Style, optional): The style of the widget.
            layout_size (int, optional): The size of the widget. Defaults to 10.
        """

        super().__init__(name=name or self.__class__.__name__)
        self.text = text
        self.layout_size = layout_size
        self.style = style

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_focus(self) -> None:
        self.has_focus = True

    def on_blur(self) -> None:
        self.has_focus = False

    def render(self) -> RenderableType:

        return Align.center(
            renderable=FigletTextRenderable(text=self.text),
            vertical="middle",
            style=self.style or "",
            pad=False,
        )

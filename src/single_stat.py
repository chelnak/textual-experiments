from __future__ import annotations
from random import choice

from rich.color import ANSI_COLOR_NAMES
from rich.console import RenderableType
from rich.panel import Panel
from rich.align import Align
from rich import box
from rich.style import Style

from textual.app import App
from textual.widget import Widget
from textual.reactive import Reactive, watch

from .figlet_widget import FigletTextRenderable


class SingleStatWidget(Widget):
    """The digital display of the calculator."""

    value: Reactive[int] = Reactive(0)

    def __init__(self, name: str | None):
        """Initialize the calculator display."""
        super().__init__(name=name)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        watch(self, "value", self.refresh)

    def render(self) -> RenderableType:
        """Build a Rich renderable to render the calculator display."""
        color = choice(list(ANSI_COLOR_NAMES.keys()))

        return Panel(
            renderable=Align.center(
                FigletTextRenderable(str(self.value)),
                vertical="middle",
                style=Style(color=color),
            ),
            box=box.DOUBLE,
            width=40,
            title=self.name,
        )


class SingleStatApp(App):
    async def on_mount(self) -> None:

        grid = await self.view.dock_grid()

        grid.add_column("col", max_size=30)
        grid.add_row("row", size=10)
        grid.set_repeat(True, False)

        stat_one = SingleStatWidget("one")
        stat_one.value = 10
        grid.place(stat_one)

        stat_two = SingleStatWidget("two")
        stat_two.value = 20
        grid.place(stat_two)

        def update_widgets():
            stat_one.value = stat_one.value + 1
            stat_two.value = stat_two.value + 1

        self.set_interval(10, update_widgets)


if __name__ == "__main__":
    """Single stat widgets.
    They will update every 10 seconds with an incremented number and a new colour.
    """
    SingleStatApp.run(title="AutoComplete", log="textual.log")

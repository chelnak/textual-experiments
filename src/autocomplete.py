from __future__ import annotations

from typing import Any
from random import choice

from rich.align import Align
from rich.console import RenderableType
from rich.text import Text
from rich.style import Style
from rich.color import ANSI_COLOR_NAMES

from textual.app import App
from textual.widget import Widget
from textual.reactive import Reactive
from textual import events
from textual.message import Message, MessageTarget
from textual_inputs import TextInput

from fast_autocomplete.misc import read_csv_gen
from fast_autocomplete import AutoComplete

from .figlet_widget import FigletTextWidget


WAITING_FOR_INPUT = Text.from_markup("✏️ [b]...[/]")


def replace_last(string: str, find: str, replace: str) -> str:
    """Replace the last occurrence of a string."""
    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]


class WordClicked(Message):
    """An message used to notify a consumer that a word has been clicked in the ui."""

    def __init__(self, sender: MessageTarget, word: str) -> None:
        self.word = word
        super().__init__(sender)


class ResultsWidget(Widget):
    """A widget that displays a list of words."""

    values: Reactive[list[str]] = Reactive([])
    hover_word: Reactive[int | None] = Reactive(None)

    def get_word(self, id: int, word: str) -> Text:
        """Formats a given word for the renderable."""
        color = choice(list(ANSI_COLOR_NAMES.keys()))
        meta = {"@click": f"click_word({id})", "word_id": id}

        renderable = Text(f"{word}", style=Style(color=color, meta=meta))

        if self.hover_word == id:
            renderable.stylize(Style(color="black", bgcolor="grey82"))
        renderable.append(" ")

        return renderable

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        """Handle mouse move events."""
        self.hover_word = event.style.meta.get("word_id")

    async def action_click_word(self, word_id: int) -> None:
        """Posts a message when a word is clicked."""
        word = self.values[word_id]
        await self.post_message_from_child(WordClicked(self, word))

    def render(self) -> RenderableType:
        """Render the widget."""
        results = []

        if self.values:
            for i, v in enumerate(self.values):
                results.append(self.get_word(i, v))
        else:
            results.append(WAITING_FOR_INPUT)

        return Align.center(Text.assemble(*results), vertical="top")


class PredictiveTextInputWidget(TextInput):

    value: Reactive[str] = Reactive("")
    prediction: Reactive[str] = Reactive("")
    last_word: Reactive[str] = Reactive("")

    async def on_key(self, event: events.Key) -> None:

        if event.key == "ctrl+i":
            self.log(f"tab pressed: {self.prediction}")
            self.value = replace_last(self.value, self.last_word, self.prediction)
            self._cursor_position = len(self.value)
            self.last_word = self.prediction
            await self._emit_on_change(event)

    def _render_text_with_cursor(self) -> list[str | tuple[str, Style]]:
        """
        Produces the renderable Text object combining value and cursor
        """

        if len(self.value) == 0:
            segments = [self.cursor]

        elif self._cursor_position == 0:
            segments = [self.cursor, self._conceal_or_reveal(self.value)]

        elif self._cursor_position == len(self.value):
            prediction: str | Text = ""
            if len(self.prediction) > 0:

                words = self.value.split()
                if len(words) > 1:
                    self.last_word = words[-1]
                else:
                    self.last_word = self.value

                if self.prediction != self.last_word and not self.value.endswith(" "):
                    prediction = Text(
                        self.prediction[len(self.last_word) :],
                        style=Style(dim=True, color="green"),
                    )
                else:
                    prediction = ""

            segments = [self.value, self.cursor, prediction]

        else:

            segments = [
                self._conceal_or_reveal(self.value[: self._cursor_position]),
                self.cursor,
                self._conceal_or_reveal(self.value[self._cursor_position :]),
            ]

        return segments


class AutoCompleter(App):

    input: PredictiveTextInputWidget
    placeholder: Reactive[str] = Reactive("")
    autocompleter: AutoComplete = None

    def get_words(self) -> dict[str, Any]:
        """Get the words from the csv file.
        In this case we are loading in a list of animals..
        """
        words: dict[str, Any] = {}
        csv = read_csv_gen("animals.txt")
        for word in csv:
            words[word[0].lower()] = {}

        return words

    async def on_load(self) -> None:
        """Actions that happen when the app first loads."""
        words = self.get_words()
        self.autocompleter = AutoComplete(words=words)
        self.input = PredictiveTextInputWidget()
        self.results = ResultsWidget()

    async def on_mount(self) -> None:
        """Actions that happen when the a mount event occurs."""
        grid = await self.view.dock_grid()

        grid.add_column("col", max_size=100)
        grid.add_row("row", size=3)
        grid.set_repeat(False, True)
        grid.add_areas(
            title="col,row-1-start|row-3-end",
            center="col,row-4",
            results="col,row-5-start|row-7-end",
        )
        grid.set_align("center", "center")

        grid.place(title=FigletTextWidget(text="Animals"))
        grid.place(center=self.input)
        grid.place(results=self.results)

        await self.input.focus()

    async def handle_word_clicked(self, message: WordClicked) -> None:
        """Handle a WordClicked message."""
        self.log(f"Word clicked {message.word} ")
        current_string = self.input.value.split(" ")[-1]

        self.input.value = replace_last(self.input.value, current_string, message.word)
        self.input._cursor_position = len(self.input.value)
        await self.input.focus()
        self.refresh()

    async def handle_input_on_change(self) -> None:
        """Handle an InputOnChange message."""
        if not self.input.value:
            self.results.values = [WAITING_FOR_INPUT]
            return

        search_string = self.input.value.split(" ")[-1]

        search_result = self.autocompleter.get_tokens_flat_list(
            word=search_string, max_cost=2, size=5
        )

        if search_result:
            self.results.values = search_result
            self.input.prediction = search_result[0]

        elif not search_result and not search_string:
            self.results.values = [WAITING_FOR_INPUT]
        else:
            self.results.values = ["😔"]

        self.refresh()


if __name__ == "__main__":
    """A demo app that shows how it might be possible to implement a simple autocomplete solution with textual.

    Apart from Textual and Rich these resources were also used:

    textual-inputs: https://github.com/sirfuzzalot/textual-inputs
    fast-autocomplete: https://github.com/seperman/fast-autocomplete
    animals.txt: https://gist.github.com/atduskgreg/3cf8ef48cb0d29cf151bedad81553a54
    Replacing the last occurrence of a string: https://bytenota.com/python-replace-last-occurrence-of-a-string/

    """
    AutoCompleter.run(title="AutoComplete", log="textual.log")

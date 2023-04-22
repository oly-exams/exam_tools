# pylint: disable=unused-import

import os

from ipho_exam.models import (
    Figure,
    CompiledFigure,
    RawFigure,
    VALID_RAW_FIGURE_EXTENSIONS,
    VALID_COMPILED_FIGURE_EXTENSIONS,
)

from ipho_exam.utils import natural_id
from .base_data import BaseDataCreator


class FigureDataCreator(BaseDataCreator):
    def create_figure(self, *, name, fig_id, filename, params=""):
        extension = os.path.splitext(filename)[1]
        with self.full_path(filename).open("rb") as fig_file:
            if extension in VALID_COMPILED_FIGURE_EXTENSIONS:
                fig, created = CompiledFigure.objects.get_or_create(
                    name=name, fig_id=fig_id, params=params
                )
                fig.content = str(fig_file.read(), "utf-8")
            elif extension in VALID_RAW_FIGURE_EXTENSIONS:
                fig, created = RawFigure.objects.get_or_create(
                    content=fig_file.read(),
                    name=name,
                    fig_id=fig_id,
                    filetype=extension.lstrip("."),
                )
            else:
                raise ValueError(f"Extension {extension} not valid.")

        if created:
            fig.save()
            self.log(fig, "..", "created")
        return fig

    def create_figure_from_file(self, *, filename, params=""):
        self.create_figure(
            name=os.path.splitext(os.path.split(filename)[1])[0],
            fig_id=natural_id.generate_id,
            filename=filename,
            params=params,
        )

    def create_figures_from_folder(self, *, folder="figures", params=""):
        # pylint: disable=unused-argument
        for filename in os.listdir(self.full_path(folder)):
            self.create_figure_from_file(filename=os.path.join(folder, filename))

    def create_figures_with_ids(self, *, fig_ids, filename, params=""):
        for fig_id in fig_ids:
            self.create_figure(
                name=fig_id, fig_id=fig_id, filename=filename, params=params
            )

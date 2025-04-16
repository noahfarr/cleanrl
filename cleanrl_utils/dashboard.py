import numpy as np
from rich import box
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from time import sleep
from argparse import Namespace


class Dashboard:
    def __init__(self, run_id: str, args: Namespace):
        self.run_id = run_id
        self.args = args

        self.SPS = 0
        self.global_step = 0
        self.episodic_return = 0
        self.episodic_length = 0
        self.losses = {}

        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TimeRemainingColumn(),
            expand=True,
        )
        self.task = self.progress.add_task("Progress", total=self.args.total_timesteps)

    def get_dashboard(
        self,
    ) -> Table:

        dashboard = Table(
            box=box.ROUNDED,
            expand=True,
            show_header=False,
            border_style="white",
        )

        header = Table(box=None, expand=True, show_header=False)
        header.add_column(justify="left")
        header_text = f"[bold white]{self.args.exp_name} - {self.run_id}[/]"
        header.add_row(header_text)
        dashboard.add_row(header)

        summary_table = Table(box=None, expand=True)
        summary_table.add_column(
            "Summary", justify="left", vertical="top", width=16, style="white"
        )
        summary_table.add_column(
            "Value", justify="right", vertical="top", width=8, style="white"
        )
        summary_table.add_row("Environment", f"{self.args.env_id}", style="white")
        summary_table.add_row(
            "Total Timesteps", f"{self.args.total_timesteps}", style="white"
        )
        summary_table.add_row("Global Step", f"{self.global_step}", style="white")
        summary_table.add_row("SPS", f"{self.SPS}", style="white")

        losses_table = Table(box=None, expand=True)
        losses_table.add_column("Losses", justify="left", width=16, style="white")
        losses_table.add_column("Value", justify="right", width=8, style="white")
        for metric, value in self.losses.items():
            losses_table.add_row(metric, f"{value}")

        monitor = Table(box=None, expand=True, pad_edge=False)
        monitor.add_row(summary_table, losses_table)
        dashboard.add_row(monitor)

        statistics = Table(box=None, expand=True, pad_edge=False)
        left_stats = Table(box=None, expand=True)
        right_stats = Table(box=None, expand=True)
        left_stats.add_column("Stats", justify="left", width=20, style="yellow")
        left_stats.add_column("Value", justify="right", width=10, style="green")
        right_stats.add_column("Stats", justify="left", width=20, style="yellow")
        right_stats.add_column("Value", justify="right", width=10, style="green")
        left_stats.add_row("Episodic Return", f"{self.episodic_return}")
        right_stats.add_row("Episodic Length", f"{self.episodic_length}")
        statistics.add_row(left_stats, right_stats)
        dashboard.add_row(statistics)

        dashboard.add_row("")
        self.progress.update(self.task, completed=int(self.global_step))
        dashboard.add_row(self.progress)

        return dashboard

    def log(self, live, **kwargs):
        self.global_step = kwargs.get("global_step", self.global_step)
        self.SPS = kwargs.get("SPS", self.SPS)
        self.episodic_return = kwargs.get("episodic_return", self.episodic_return)
        self.episodic_length = kwargs.get("episodic_length", self.episodic_length)
        self.losses = kwargs.get("losses", self.losses)
        dashboard = self.get_dashboard()
        live.update(dashboard)

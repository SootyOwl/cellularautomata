"""Click command line interface for cellular automata.

Has options for:
"ruleset": ruleset,
"seed": seed,
"width": width,
"height": height,
"cell_size": cell_size,
"num_states": num_states,
"fps": fps,
"run_seconds": run_seconds,
"output_to_video": output_to_video,
# RainbowLife2 only
"equality_threshold": equality_threshold"""

import json
import time
import click
import random
from cellularautomata.game import GameMP4, Game
from cellularautomata.ca import CellularAutomata, CellularAutomataMP
from cellularautomata.rules2 import RainbowLife2, RainbowLife, RainbowLife3


RULES = {
    "RainbowLife": RainbowLife,
    "RainbowLife2": RainbowLife2,
    "RainbowLife3": RainbowLife3,
}


def runner(ruleset, seed, width, height, cell_size, num_states, fps, run_seconds, output_to_video, equality_threshold):
    """Run a cellular automata game."""
    rules = RULES[ruleset](
        seed=seed,
        num_states=num_states, 
        pastel=True, 
        scroll=False,
        equality_threshold=equality_threshold
    )
    if output_to_video:
        game = GameMP4(
            width=width, 
            height=height, 
            cell_size=cell_size, 
            rules=rules, 
            fps=fps, 
            run_seconds=run_seconds
        )
    else:
        game = Game(
            width=width, 
            height=height, 
            cell_size=cell_size, 
            rules=rules, 
            fps=fps
        )
    game.run()
    if output_to_video:
        output(game, ruleset, seed, width, height, cell_size, num_states, fps, run_seconds, equality_threshold)


def output(game, ruleset, seed, width, height, cell_size, num_states, fps, run_seconds, equality_threshold):
    """Pop up a little save y/n dialog box."""
    import os
    
    if not click.confirm("Save video?"):
        click.echo("Not saving video.")
        os.remove("output.mp4")
        return
    
    # generate a filename from configuration and rules class name
    rules_name = game.ca.rules.__class__.__name__
    filename = f"videos/{rules_name}_{seed}_{width}x{height}_{cell_size}_{num_states}_{fps}_{run_seconds}_{equality_threshold}_{time.time()}.mp4"
    # create videos directory if it doesn't exist
    os.makedirs("videos", exist_ok=True)
    os.rename("output.mp4", filename)
    click.echo(f"Saved to {filename}")
    summary(RULES[ruleset], filename, seed=seed, width=width, height=height, cell_size=cell_size, num_states=num_states, fps=fps, run_seconds=run_seconds, equality_threshold=equality_threshold)


def summary(rules, filename, **kwargs):
    """Print a summary of the game."""
    summary = f"""{str(rules)}

Configuration dict:
{json.dumps(kwargs, indent=2)}

Video saved as {filename}
"""
    click.echo(summary)
    summary_filename = filename.replace(".mp4", ".txt")
    with open(summary_filename, "w") as f:
        f.write(summary)   


@click.command()
@click.option("--ruleset", type=click.Choice(RULES.keys()), default="RainbowLife2", show_default=True)
@click.option("--seed", type=int, default=random.randint(0, 1000000))
@click.option("--width", type=int, default=1000, show_default=True)
@click.option("--height", type=int, default=1000, show_default=True)
@click.option("--cell_size", type=int, default=20, show_default=True)
@click.option("--num_states", type=int, default=50, show_default=True)
@click.option("--fps", type=int, default=30, show_default=True)
@click.option("--run_seconds", type=int, default=60, show_default=True)
# boolean flags
@click.option("--output_to_video", is_flag=True, default=True, show_default=True)
@click.option("--use_mp", is_flag=True, default=False, show_default=True)
# RainbowLife2 only
@click.option("--equality_threshold", type=int, default=0, show_default=True)
def main(ruleset, seed, width, height, cell_size, num_states, fps, run_seconds, output_to_video, use_mp, equality_threshold):
    """Run a cellular automata game."""
    rules = RULES[ruleset](
        seed=seed,
        num_states=num_states, 
        pastel=True, 
        scroll=False,
        equality_threshold=equality_threshold
    )
    if use_mp:
        ca = CellularAutomataMP(width // cell_size, height // cell_size, rules)
    else:
        ca = CellularAutomata(width // cell_size, height // cell_size, rules)

    if output_to_video:
        game = GameMP4(
            width=width, 
            height=height, 
            cell_size=cell_size, 
            rules=rules, 
            fps=fps, 
            run_seconds=run_seconds,
            ca=ca
        )
    else:
        game = Game(
            width=width, 
            height=height, 
            cell_size=cell_size, 
            rules=rules, 
            fps=fps,
            ca=ca
        )
    game.run()
    if output_to_video:
        output(game, ruleset, seed, width, height, cell_size, num_states, fps, run_seconds, equality_threshold)
    else:
        click.echo("Not saving video.")
        click.echo(f"Ruleset: {ruleset}")
        click.echo(f"Seed: {seed}")
        click.echo(f"Width: {width}")
        click.echo(f"Height: {height}")
        click.echo(f"Cell size: {cell_size}")
        click.echo(f"Number of states: {num_states}")
        click.echo(f"FPS: {fps}")
        click.echo(f"Run seconds: {run_seconds}")
        click.echo(f"Equality threshold: {equality_threshold}") if ruleset == "RainbowLife2" else None
        click.echo("Done.")
        click.echo("")


if __name__ == "__main__":
    main()